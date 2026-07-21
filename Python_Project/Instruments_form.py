"""
Instruments_form.py

CRUD form for the Instruments table (the central instrumentation register).

This table has ~100 columns and 7 foreign keys, so — following the same
metadata-driven approach used for SpareParts_form — fields are declared once
in FIELD_TABS and rendered generically into a ttk.Notebook, instead of one
flat form or one hand-written widget block per column.

Conventions carried over from the rest of the project:
    - get_connection() from db_connection (pyodbc / ODBC Driver 17 / Windows Auth)
    - FK comboboxes show a human-readable label, store the integer ID
    - Nullable dates use a "Set" checkbox + tkcalendar DateEntry
    - pyodbc.IntegrityError caught separately for meaningful constraint messages
    - Dynamic FK-dependency check on delete using sys.foreign_keys
    - Computed columns (IsUnderWarranty, CalibrationStatus) are read-only /
      excluded from INSERT/UPDATE since SQL Server computes them
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date

import pyodbc
from tkcalendar import DateEntry

from db_connection import get_connection


# ----------------------------------------------------------------------
# Field metadata
# Each field: (column, label, field_type, extra)
#   field_type one of:
#     "text"      - single-line NVARCHAR/VARCHAR
#     "multiline" - long NVARCHAR (Text widget)
#     "int"       - INT
#     "decimal"   - DECIMAL (kept as string, validated as float)
#     "bit"       - BIT (checkbutton)
#     "date"      - DATE/DATETIME, nullable, "Set" checkbox + DateEntry
#     "combo"     - free-editable combobox with suggested values (extra=list)
#     "fk"        - foreign key combobox (extra=lookup key into FK_LOOKUPS)
# ----------------------------------------------------------------------

FK_LOOKUPS = {
    "SiteID": {
        "query": "SELECT SiteID, SiteName FROM Sites ORDER BY SiteName",
        "format": lambda r: r[1],
    },
    "UnitID": {
        "query": """
            SELECT pu.UnitID, pu.UnitName, pu.UnitCode, s.SiteName
            FROM ProcessUnits pu
            LEFT JOIN Sites s ON pu.SiteID = s.SiteID
            ORDER BY s.SiteName, pu.UnitName
        """,
        "format": lambda r: f"{r[1]} ({r[2]}) - {r[3] or 'No Site'}",
    },
    "SubSystemID": {
        "query": "SELECT SubSystemID, SubSystemName, SubSystemCode FROM SubSystems ORDER BY SubSystemName",
        "format": lambda r: f"{r[1]} ({r[2]})",
    },
    "SystemID": {
        "query": "SELECT SystemID, SystemName, SystemCode FROM ControlSystems ORDER BY SystemName",
        "format": lambda r: f"{r[1]} ({r[2]})",
    },
    "InstrumentTypeID": {
        "query": "SELECT InstrumentTypeID, TypeName, TypeCode FROM InstrumentTypes ORDER BY TypeCode",
        "format": lambda r: f"{r[2]} - {r[1]}",
    },
    "ManufacturerID": {
        "query": "SELECT ManufacturerID, ManufacturerName FROM Manufacturers ORDER BY ManufacturerName",
        "format": lambda r: r[1],
    },
    "RedundantPair": {
        "query": "SELECT InstrumentID, TagNumber FROM Instruments ORDER BY TagNumber",
        "format": lambda r: r[1],
    },
}

STATUS_VALUES = ["Operational", "Standby", "Maintenance", "Faulty", "Bypassed", "Decommissioned"]
CRITICALITY_VALUES = ["Low", "Medium", "High", "Critical"]

FIELD_TABS = [
    ("Identification & Location", [
        ("TagNumber", "Tag Number *", "text", None),
        ("AlternateTag", "Alternate Tag", "text", None),
        ("SerialNumber", "Serial Number", "text", None),
        ("AssetNumber", "Asset Number", "text", None),
        ("SiteID", "Site *", "fk", "SiteID"),
        ("UnitID", "Process Unit *", "fk", "UnitID"),
        ("SubSystemID", "Sub-System", "fk", "SubSystemID"),
        ("SystemID", "Control System", "fk", "SystemID"),
    ]),
    ("Classification & Technical", [
        ("InstrumentTypeID", "Instrument Type *", "fk", "InstrumentTypeID"),
        ("ManufacturerID", "Manufacturer (Lookup)", "fk", "ManufacturerID"),
        ("Manufacturer", "Manufacturer (Free Text)", "text", None),
        ("Model", "Model", "text", None),
        ("Description", "Description", "multiline", None),
        ("FunctionalDescription", "Functional Description", "multiline", None),
    ]),
    ("Process Info", [
        ("ProcessVariable", "Process Variable", "text", None),
        ("ServiceDescription", "Service Description", "text", None),
        ("FluidType", "Fluid Type", "text", None),
        ("FluidComposition", "Fluid Composition", "text", None),
        ("MeasurementRangeMin", "Measurement Range Min", "decimal", None),
        ("MeasurementRangeMax", "Measurement Range Max", "decimal", None),
        ("MeasurementUnit", "Measurement Unit", "text", None),
        ("OutputRangeMin", "Output Range Min", "decimal", None),
        ("OutputRangeMax", "Output Range Max", "decimal", None),
        ("OutputUnit", "Output Unit", "text", None),
    ]),
    ("Performance", [
        ("Accuracy", "Accuracy", "text", None),
        ("Repeatability", "Repeatability", "text", None),
        ("Rangeability", "Rangeability", "text", None),
        ("ResponseTime", "Response Time", "text", None),
    ]),
    ("Installation", [
        ("LocationDescription", "Location Description", "text", None),
        ("InstallationDrawing", "Installation Drawing", "text", None),
        ("PIDNumber", "P&ID Number", "text", None),
        ("PipelineID", "Pipeline ID", "text", None),
        ("ElevationLevel", "Elevation Level", "text", None),
        ("GridReference", "Grid Reference", "text", None),
        ("MountingType", "Mounting Type", "text", None),
        ("ProcessConnection", "Process Connection", "text", None),
        ("MaterialOfConstruction", "Material of Construction", "text", None),
        ("WetPartsMaterial", "Wet Parts Material", "text", None),
        ("GasketMaterial", "Gasket Material", "text", None),
    ]),
    ("Electrical", [
        ("PowerSupply", "Power Supply", "text", None),
        ("PowerConsumption", "Power Consumption", "text", None),
        ("SignalType", "Signal Type", "text", None),
        ("CommunicationProtocol", "Communication Protocol", "text", None),
        ("WiringDiagram", "Wiring Diagram", "text", None),
        ("JunctionBoxNumber", "Junction Box Number", "text", None),
        ("CableTag", "Cable Tag", "text", None),
        ("CableType", "Cable Type", "text", None),
        ("CableLength_Meters", "Cable Length (m)", "decimal", None),
    ]),
    ("I/O Assignment", [
        ("IOCardLocation", "I/O Card Location", "text", None),
        ("IOCardType", "I/O Card Type", "text", None),
        ("DCSAddress", "DCS Address", "text", None),
        ("ModbusAddress", "Modbus Address", "int", None),
    ]),
    ("Safety & Hazardous Area", [
        ("IsSafetyInstrument", "Safety Instrument", "bit", None),
        ("SIL_Rating", "SIL Rating", "text", None),
        ("SIF_Number", "SIF Number", "text", None),
        ("ATEX_Rating", "ATEX Rating", "text", None),
        ("ATEX_Certificate", "ATEX Certificate", "text", None),
        ("IP_Rating", "IP Rating", "text", None),
        ("NEMA_Rating", "NEMA Rating", "text", None),
        ("IECEx_Rating", "IECEx Rating", "text", None),
    ]),
    ("Alarms & Redundancy", [
        ("HasAlarm", "Has Alarm", "bit", None),
        ("AlarmCount", "Alarm Count", "int", None),
        ("HasTrip", "Has Trip", "bit", None),
        ("TripCount", "Trip Count", "int", None),
        ("IsInterlock", "Is Interlock", "bit", None),
        ("IsRedundant", "Is Redundant", "bit", None),
        ("RedundantPair", "Redundant Pair (Instrument)", "fk", "RedundantPair"),
        ("RedundancyType", "Redundancy Type", "text", None),
    ]),
    ("Status & Criticality", [
        ("Status", "Status", "combo", STATUS_VALUES),
        ("IsOperational", "Is Operational", "bit", None),
        ("IsByPassed", "Is Bypassed", "bit", None),
        ("ByPassReason", "Bypass Reason", "text", None),
        ("ByPassDate", "Bypass Date", "date", None),
        ("ByPassApprovedBy", "Bypass Approved By", "text", None),
        ("Criticality", "Criticality", "combo", CRITICALITY_VALUES),
        ("FMEA_RPN", "FMEA RPN", "int", None),
        ("MaintenancePriority", "Maintenance Priority", "text", None),
    ]),
    ("Purchase & Warranty", [
        ("PurchaseDate", "Purchase Date", "date", None),
        ("PurchaseOrderNumber", "Purchase Order Number", "text", None),
        ("PurchaseCost", "Purchase Cost", "decimal", None),
        ("CostCurrency", "Cost Currency", "text", None),
        ("DeliveryDate", "Delivery Date", "date", None),
        ("InstallationDate", "Installation Date", "date", None),
        ("CommissionDate", "Commission Date", "date", None),
        ("StartupDate", "Startup Date", "date", None),
        ("WarrantyPeriod_Months", "Warranty Period (months)", "int", None),
        ("WarrantyStartDate", "Warranty Start Date", "date", None),
        ("WarrantyExpiryDate", "Warranty Expiry Date", "date", None),
    ]),
    ("Calibration", [
        ("CalibrationRequired", "Calibration Required", "bit", None),
        ("CalibrationInterval_Days", "Calibration Interval (days)", "int", None),
        ("LastCalibrationDate", "Last Calibration Date", "date", None),
        ("CalibrationDueDate", "Calibration Due Date", "date", None),
        ("NextCalibrationDate", "Next Calibration Date", "date", None),
        ("TotalCalibrationsPerformed", "Total Calibrations Performed", "int", None),
    ]),
    ("Maintenance & Reliability", [
        ("MaintenanceInterval_Days", "Maintenance Interval (days)", "int", None),
        ("LastMaintenanceDate", "Last Maintenance Date", "date", None),
        ("NextMaintenanceDate", "Next Maintenance Date", "date", None),
        ("TotalMaintenancePerformed", "Total Maintenance Performed", "int", None),
        ("InstallationRunningHours", "Installation Running Hours", "int", None),
        ("TotalFailures", "Total Failures", "int", None),
        ("MTBF_Hours", "MTBF (Hours)", "decimal", None),
        ("MTTR_Hours", "MTTR (Hours)", "decimal", None),
        ("Availability_Percent", "Availability (%)", "decimal", None),
    ]),
    ("Documentation", [
        ("DatasheetPath", "Datasheet Path", "text", None),
        ("ManualPath", "Manual Path", "text", None),
        ("DrawingPath", "Drawing Path", "text", None),
        ("CertificatePath", "Certificate Path", "text", None),
    ]),
    ("Loop Details", [
        ("LoopNumber", "Loop Number", "text", None),
        ("LoopDiagram", "Loop Diagram", "text", None),
        ("IsPartOfControlLoop", "Is Part of Control Loop", "bit", None),
        ("ControllerTag", "Controller Tag", "text", None),
        ("FinalControlElement", "Final Control Element", "text", None),
    ]),
    ("Additional Info", [
        ("SpecialRequirements", "Special Requirements", "multiline", None),
        ("OperatingInstructions", "Operating Instructions", "multiline", None),
        ("SafetyNotes", "Safety Notes", "multiline", None),
        ("Notes", "Notes", "multiline", None),
    ]),
    ("Audit Trail", [
        ("CreatedBy", "Created By", "text", None),
        ("ModifiedBy", "Modified By", "text", None),
    ]),
]

# Columns computed by SQL Server (never sent on INSERT/UPDATE, never editable)
COMPUTED_COLUMNS = {"IsUnderWarranty", "CalibrationStatus"}

# Columns SQL Server sets automatically (default/GETDATE()) - not sent on INSERT
SERVER_DEFAULTED_ON_INSERT = {"CreatedDate", "ModifiedDate"}


class InstrumentsForm(ttk.Frame):
    TABLE_NAME = "Instruments"

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.selected_id = None
        self.fk_lookups = {key: {} for key in FK_LOOKUPS}   # key -> {display: id}
        self.field_widgets = {}   # column -> dict with widget refs / vars

        self._build_ui()
        self._load_all_fk_lookups()
        self.refresh_data()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------
    def _build_ui(self):
        # ---------------- Filter panel ----------------
        filter_frame = ttk.LabelFrame(self, text="Search / Filter")
        filter_frame.pack(side="top", fill="x", padx=8, pady=(8, 4))

        ttk.Label(filter_frame, text="Search Column:").grid(row=0, column=0, sticky="w", padx=5, pady=4)
        self.search_column_var = tk.StringVar(value="(All Columns)")
        self.search_column_combo = ttk.Combobox(
            filter_frame, textvariable=self.search_column_var, state="readonly", width=20,
            values=["(All Columns)", "TagNumber", "SerialNumber", "AssetNumber",
                    "Model", "Description", "ServiceDescription"]
        )
        self.search_column_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=4)

        ttk.Label(filter_frame, text="Keyword:").grid(row=0, column=2, sticky="w", padx=5, pady=4)
        self.search_text_var = tk.StringVar()
        search_entry = ttk.Entry(filter_frame, textvariable=self.search_text_var, width=28)
        search_entry.grid(row=0, column=3, sticky="ew", padx=5, pady=4)
        search_entry.bind("<KeyRelease>", lambda e: self.refresh_data())

        ttk.Label(filter_frame, text="Status:").grid(row=1, column=0, sticky="w", padx=5, pady=4)
        self.status_filter_var = tk.StringVar(value="(All)")
        ttk.Combobox(
            filter_frame, textvariable=self.status_filter_var, state="readonly", width=20,
            values=["(All)"] + STATUS_VALUES
        ).grid(row=1, column=1, sticky="ew", padx=5, pady=4)
        self.status_filter_var.trace_add("write", lambda *a: self.refresh_data())

        btn_frame = ttk.Frame(filter_frame)
        btn_frame.grid(row=2, column=0, columnspan=4, sticky="w", padx=5, pady=(0, 4))
        ttk.Button(btn_frame, text="Apply Filter", command=self.refresh_data).pack(side="left", padx=3)
        ttk.Button(btn_frame, text="Clear Filter", command=self._clear_filter).pack(side="left", padx=3)

        for col in range(4):
            filter_frame.columnconfigure(col, weight=1)

        # ---------------- Treeview ----------------
        tree_frame = ttk.Frame(self)
        tree_frame.pack(side="top", fill="both", expand=True, padx=8, pady=4)

        columns = ("InstrumentID", "TagNumber", "Description", "InstrumentType",
                   "Status", "Criticality")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=9)
        headings = {
            "InstrumentID": "ID", "TagNumber": "Tag Number", "Description": "Description",
            "InstrumentType": "Type", "Status": "Status", "Criticality": "Criticality",
        }
        widths = {
            "InstrumentID": 50, "TagNumber": 110, "Description": 260,
            "InstrumentType": 110, "Status": 100, "Criticality": 90,
        }
        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor="w")

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)

        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        # ---------------- Entry panel (Notebook of tabs) ----------------
        outer_panel = ttk.LabelFrame(self, text="Instrument Details")
        outer_panel.pack(side="top", fill="both", expand=False, padx=8, pady=4)

        # InstrumentID (disabled, identity) shown above the notebook
        id_frame = ttk.Frame(outer_panel)
        id_frame.pack(side="top", fill="x", padx=5, pady=(5, 0))
        ttk.Label(id_frame, text="Instrument ID:").pack(side="left", padx=(0, 5))
        self.id_var = tk.StringVar()
        ttk.Entry(id_frame, textvariable=self.id_var, width=15, state="disabled").pack(side="left")

        self.notebook = ttk.Notebook(outer_panel)
        self.notebook.pack(side="top", fill="both", expand=True, padx=5, pady=5)

        for tab_name, fields in FIELD_TABS:
            tab_frame = ttk.Frame(self.notebook)
            self.notebook.add(tab_frame, text=tab_name)
            self._build_tab_fields(tab_frame, fields)

        ttk.Label(outer_panel, text="* Required fields", foreground="gray").pack(
            side="top", anchor="w", padx=5, pady=(0, 4)
        )

        # Action buttons
        action_frame = ttk.Frame(outer_panel)
        action_frame.pack(side="top", fill="x", padx=5, pady=(0, 8))
        ttk.Button(action_frame, text="New", command=self._new_record).pack(side="left", padx=3)
        ttk.Button(action_frame, text="Save", command=self._save_record).pack(side="left", padx=3)
        ttk.Button(action_frame, text="Delete", command=self._delete_record).pack(side="left", padx=3)
        ttk.Button(action_frame, text="Refresh", command=self.refresh_data).pack(side="left", padx=3)
        ttk.Button(
            action_frame, text="Reload Lookups", command=self._load_all_fk_lookups
        ).pack(side="left", padx=3)

    def _build_tab_fields(self, tab_frame, fields):
        for col in range(4):
            tab_frame.columnconfigure(col, weight=1)

        row = 0
        col_pos = 0
        for column, label, field_type, extra in fields:
            label_col = col_pos * 2
            widget_col = label_col + 1

            ttk.Label(tab_frame, text=f"{label}:").grid(
                row=row, column=label_col, sticky="w", padx=5, pady=4
            )

            if field_type == "text":
                var = tk.StringVar()
                ttk.Entry(tab_frame, textvariable=var, width=26).grid(
                    row=row, column=widget_col, sticky="ew", padx=5, pady=4
                )
                self.field_widgets[column] = {"type": field_type, "var": var}

            elif field_type == "int":
                var = tk.StringVar()
                ttk.Entry(tab_frame, textvariable=var, width=26).grid(
                    row=row, column=widget_col, sticky="ew", padx=5, pady=4
                )
                self.field_widgets[column] = {"type": field_type, "var": var}

            elif field_type == "decimal":
                var = tk.StringVar()
                ttk.Entry(tab_frame, textvariable=var, width=26).grid(
                    row=row, column=widget_col, sticky="ew", padx=5, pady=4
                )
                self.field_widgets[column] = {"type": field_type, "var": var}

            elif field_type == "bit":
                var = tk.BooleanVar(value=False)
                ttk.Checkbutton(tab_frame, variable=var).grid(
                    row=row, column=widget_col, sticky="w", padx=5, pady=4
                )
                self.field_widgets[column] = {"type": field_type, "var": var}

            elif field_type == "combo":
                var = tk.StringVar()
                ttk.Combobox(
                    tab_frame, textvariable=var, width=24, values=extra
                ).grid(row=row, column=widget_col, sticky="ew", padx=5, pady=4)
                self.field_widgets[column] = {"type": field_type, "var": var}

            elif field_type == "fk":
                var = tk.StringVar()
                combo = ttk.Combobox(tab_frame, textvariable=var, state="readonly", width=28)
                combo.grid(row=row, column=widget_col, sticky="ew", padx=5, pady=4)
                self.field_widgets[column] = {"type": field_type, "var": var,
                                              "combo": combo, "lookup_key": extra}

            elif field_type == "date":
                set_var = tk.BooleanVar(value=False)
                date_frame = ttk.Frame(tab_frame)
                date_frame.grid(row=row, column=widget_col, sticky="w", padx=5, pady=4)
                entry = DateEntry(date_frame, width=13, date_pattern="yyyy-mm-dd", state="disabled")
                ttk.Checkbutton(
                    date_frame, text="Set", variable=set_var,
                    command=lambda e=entry, s=set_var: e.configure(
                        state="normal" if s.get() else "disabled"
                    )
                ).pack(side="left")
                entry.pack(side="left", padx=(5, 0))
                self.field_widgets[column] = {"type": field_type, "set_var": set_var, "entry": entry}

            elif field_type == "multiline":
                text_frame = ttk.Frame(tab_frame)
                text_frame.grid(row=row, column=widget_col, columnspan=3, sticky="ew", padx=5, pady=4)
                text_widget = tk.Text(text_frame, height=3, width=50, wrap="word")
                scroll = ttk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
                text_widget.configure(yscrollcommand=scroll.set)
                text_widget.pack(side="left", fill="both", expand=True)
                scroll.pack(side="right", fill="y")
                self.field_widgets[column] = {"type": field_type, "widget": text_widget}
                # multiline fields take a full row on their own
                row += 1
                col_pos = 0
                continue

            col_pos += 1
            if col_pos >= 2:
                col_pos = 0
                row += 1

    def _clear_filter(self):
        self.search_column_var.set("(All Columns)")
        self.search_text_var.set("")
        self.status_filter_var.set("(All)")

    # ------------------------------------------------------------------
    # FK lookups
    # ------------------------------------------------------------------
    def _load_all_fk_lookups(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()

            for key, cfg in FK_LOOKUPS.items():
                cursor.execute(cfg["query"])
                rows = cursor.fetchall()
                lookup = {}
                display_values = []
                for r in rows:
                    display = cfg["format"](r)
                    lookup[display] = r[0]
                    display_values.append(display)
                self.fk_lookups[key] = lookup

                widget_info = self.field_widgets.get(key)
                if widget_info and "combo" in widget_info:
                    widget_info["combo"]["values"] = display_values

            conn.close()

        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to load lookup data:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error while loading lookups:\n{e}")

    def _display_for_fk(self, lookup_key, value_id):
        if value_id is None:
            return ""
        for display, iid in self.fk_lookups.get(lookup_key, {}).items():
            if iid == value_id:
                return display
        return f"[ID {value_id}]"

    # ------------------------------------------------------------------
    # Data loading / search (treeview - summary columns only)
    # ------------------------------------------------------------------
    def refresh_data(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()

            query = """
                SELECT i.InstrumentID, i.TagNumber, i.Description,
                       it.TypeCode, i.Status, i.Criticality
                FROM Instruments i
                LEFT JOIN InstrumentTypes it ON i.InstrumentTypeID = it.InstrumentTypeID
                WHERE 1=1
            """
            params = []

            keyword = self.search_text_var.get().strip()
            if keyword:
                column = self.search_column_var.get()
                like_value = f"%{keyword}%"
                searchable_columns = ["TagNumber", "SerialNumber", "AssetNumber",
                                      "Model", "Description", "ServiceDescription"]
                if column in searchable_columns:
                    query += f" AND i.{column} LIKE ?"
                    params.append(like_value)
                else:
                    conditions = " OR ".join(f"i.{c} LIKE ?" for c in searchable_columns)
                    query += f" AND ({conditions})"
                    params.extend([like_value] * len(searchable_columns))

            status_filter = self.status_filter_var.get()
            if status_filter and status_filter != "(All)":
                query += " AND i.Status = ?"
                params.append(status_filter)

            query += " ORDER BY i.TagNumber"

            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()

            for item in self.tree.get_children():
                self.tree.delete(item)

            for row in rows:
                instrument_id, tag_number, description, type_code, status, criticality = row
                self.tree.insert(
                    "", "end", iid=str(instrument_id),
                    values=(instrument_id, tag_number, description or "",
                            type_code or "", status or "", criticality or "")
                )

        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to load Instruments data:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error while loading data:\n{e}")

    # ------------------------------------------------------------------
    # Selection / form population
    # ------------------------------------------------------------------
    def _all_columns(self):
        cols = []
        for _, fields in FIELD_TABS:
            for column, _, _, _ in fields:
                cols.append(column)
        return cols

    def _on_select(self, event):
        selection = self.tree.selection()
        if not selection:
            return

        instrument_id = int(selection[0])
        columns = self._all_columns()
        try:
            conn = get_connection()
            cursor = conn.cursor()
            col_list = ", ".join(f"[{c}]" for c in columns)
            cursor.execute(
                f"SELECT InstrumentID, {col_list} FROM Instruments WHERE InstrumentID = ?",
                (instrument_id,)
            )
            row = cursor.fetchone()
            conn.close()

            if not row:
                return

            self.selected_id = row[0]
            self.id_var.set(str(row[0]))

            for column, value in zip(columns, row[1:]):
                widget_info = self.field_widgets[column]
                ftype = widget_info["type"]

                if ftype == "fk":
                    widget_info["var"].set(self._display_for_fk(widget_info["lookup_key"], value))
                elif ftype == "bit":
                    widget_info["var"].set(bool(value))
                elif ftype == "date":
                    if value:
                        widget_info["set_var"].set(True)
                        widget_info["entry"].configure(state="normal")
                        widget_info["entry"].set_date(value)
                    else:
                        widget_info["set_var"].set(False)
                        widget_info["entry"].configure(state="disabled")
                elif ftype == "multiline":
                    widget_info["widget"].delete("1.0", tk.END)
                    if value:
                        widget_info["widget"].insert("1.0", value)
                elif ftype in ("int", "decimal", "text", "combo"):
                    widget_info["var"].set("" if value is None else str(value))

        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to load Instrument record:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error while loading record:\n{e}")

    def _new_record(self):
        self.selected_id = None
        self.id_var.set("")

        for column, widget_info in self.field_widgets.items():
            ftype = widget_info["type"]
            if ftype == "fk":
                widget_info["var"].set("")
            elif ftype == "bit":
                widget_info["var"].set(False)
            elif ftype == "date":
                widget_info["set_var"].set(False)
                widget_info["entry"].configure(state="disabled")
            elif ftype == "multiline":
                widget_info["widget"].delete("1.0", tk.END)
            else:
                widget_info["var"].set("")

        self.tree.selection_remove(self.tree.selection())

    # ------------------------------------------------------------------
    # Save (Insert / Update)
    # ------------------------------------------------------------------
    def _collect_values(self):
        """
        Returns (columns, values) ready for INSERT/UPDATE, or None if
        validation failed (a messagebox has already been shown).
        """
        columns = []
        values = []

        for tab_name, fields in FIELD_TABS:
            for column, label, field_type, extra in fields:
                widget_info = self.field_widgets[column]

                if field_type == "fk":
                    display = widget_info["var"].get().strip()
                    value = self.fk_lookups.get(widget_info["lookup_key"], {}).get(display) \
                        if display else None
                    if label.endswith("*") and value is None:
                        messagebox.showwarning("Validation", f"Please select a value for {label}")
                        return None

                elif field_type == "bit":
                    value = widget_info["var"].get()

                elif field_type == "date":
                    value = widget_info["entry"].get_date() if widget_info["set_var"].get() else None

                elif field_type == "multiline":
                    text_value = widget_info["widget"].get("1.0", tk.END).strip()
                    value = text_value or None

                elif field_type == "int":
                    raw = widget_info["var"].get().strip()
                    if raw:
                        try:
                            value = int(raw)
                        except ValueError:
                            messagebox.showwarning("Validation", f"{label} must be a whole number.")
                            return None
                    else:
                        value = None

                elif field_type == "decimal":
                    raw = widget_info["var"].get().strip()
                    if raw:
                        try:
                            value = float(raw)
                        except ValueError:
                            messagebox.showwarning("Validation", f"{label} must be a number.")
                            return None
                    else:
                        value = None

                else:  # text / combo
                    raw = widget_info["var"].get().strip()
                    if label.endswith("*") and not raw:
                        messagebox.showwarning("Validation", f"Please enter a value for {label}")
                        return None
                    value = raw or None

                columns.append(column)
                values.append(value)

        return columns, values

    def _save_record(self):
        collected = self._collect_values()
        if collected is None:
            return
        columns, values = collected

        try:
            conn = get_connection()
            cursor = conn.cursor()

            if self.selected_id:
                set_clause = ", ".join(f"[{c}] = ?" for c in columns)
                cursor.execute(
                    f"UPDATE Instruments SET {set_clause}, ModifiedDate = GETDATE() "
                    f"WHERE InstrumentID = ?",
                    values + [self.selected_id]
                )
                conn.commit()
                messagebox.showinfo("Success", "Instrument updated successfully.")
            else:
                col_list = ", ".join(f"[{c}]" for c in columns)
                placeholders = ", ".join("?" for _ in columns)
                cursor.execute(
                    f"INSERT INTO Instruments ({col_list}) VALUES ({placeholders})",
                    values
                )
                conn.commit()
                messagebox.showinfo("Success", "Instrument added successfully.")

            conn.close()
            self.refresh_data()
            self._load_all_fk_lookups()
            self._new_record()

        except pyodbc.IntegrityError as e:
            messagebox.showerror(
                "Integrity Error",
                f"Save failed. This likely violates a unique constraint "
                f"(Tag Number must be unique) or an invalid foreign key reference:\n{e}"
            )
        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to save Instrument:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error while saving:\n{e}")

    # ------------------------------------------------------------------
    # Delete (with dynamic FK dependency check)
    # ------------------------------------------------------------------
    def _get_dependent_records(self, conn, instrument_id):
        """
        Dynamically discover every table with a FK referencing Instruments,
        then count rows that reference this InstrumentID. This avoids
        hardcoding child table names as the schema keeps growing.
        """
        dependents = []
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                OBJECT_NAME(fk.parent_object_id) AS ChildTable,
                COL_NAME(fkc.parent_object_id, fkc.parent_column_id) AS ChildColumn
            FROM sys.foreign_keys fk
            JOIN sys.foreign_key_columns fkc
                ON fk.object_id = fkc.constraint_object_id
            WHERE fk.referenced_object_id = OBJECT_ID(?)
            """,
            (self.TABLE_NAME,)
        )
        fk_rows = cursor.fetchall()

        for child_table, child_column in fk_rows:
            try:
                count_cursor = conn.cursor()
                count_cursor.execute(
                    f"SELECT COUNT(*) FROM [{child_table}] WHERE [{child_column}] = ?",
                    (instrument_id,)
                )
                count = count_cursor.fetchone()[0]
                if count > 0:
                    dependents.append((child_table, count))
            except pyodbc.Error:
                continue

        return dependents

    def _delete_record(self):
        if not self.selected_id:
            messagebox.showwarning("No Selection", "Please select an Instrument to delete.")
            return

        try:
            conn = get_connection()
            dependents = self._get_dependent_records(conn, self.selected_id)

            if dependents:
                detail = "\n".join(f"  - {table}: {count} record(s)" for table, count in dependents)
                proceed = messagebox.askyesno(
                    "Instrument In Use",
                    f"This Instrument is referenced by other records:\n\n{detail}\n\n"
                    "Deleting it may fail or orphan related data depending on your "
                    "database's FK constraints.\n\nDo you still want to attempt deletion?"
                )
                if not proceed:
                    conn.close()
                    return
            else:
                confirm = messagebox.askyesno(
                    "Confirm Delete",
                    f"Delete Instrument (ID {self.selected_id})?"
                )
                if not confirm:
                    conn.close()
                    return

            cursor = conn.cursor()
            cursor.execute("DELETE FROM Instruments WHERE InstrumentID = ?", (self.selected_id,))
            conn.commit()
            conn.close()

            messagebox.showinfo("Deleted", "Instrument deleted successfully.")
            self.refresh_data()
            self._new_record()

        except pyodbc.IntegrityError as e:
            messagebox.showerror(
                "Integrity Error",
                f"Cannot delete this Instrument because other records depend on it:\n{e}"
            )
        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to delete Instrument:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error while deleting:\n{e}")
