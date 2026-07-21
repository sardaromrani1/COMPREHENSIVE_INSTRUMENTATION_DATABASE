"""
MaintenanceRecords_form.py

CRUD form for the MaintenanceRecords table.

This table has ~55 columns across work order info, scheduling, classification,
personnel, problem description, root cause, work performed, testing, downtime,
cost, warranty, status, follow-up, permits, and documentation - so, following
the same approach used for Instruments_form, CalibrationRecords_form, and
FailureRecords_form, fields are declared once in FIELD_TABS and rendered
generically into a ttk.Notebook.

Conventions carried over from the rest of the project:
    - get_connection() from db_connection (pyodbc / ODBC Driver 17 / Windows Auth)
    - FK combobox (InstrumentID -> Instruments) shows TagNumber - Description,
      stores the integer ID
    - StartDate / CompletionDate / DowntimeStart / DowntimeEnd are DATETIME,
      nullable -> "Set" checkbox + DateEntry + HH:MM
    - ScheduledDate / RequestedDate / FollowUpDate are DATE, nullable ->
      "Set" checkbox + DateEntry
    - BIT columns WITH a DEFAULT (CalibrationPerformed, FunctionalTestPassed,
      PlannedDowntime, IsWarrantyClaim, RequiresFollowUp, PermitRequired,
      HotWorkPermit, ConfinedSpacePermit) are plain checkbuttons
    - WarrantyApproved is a BIT with NO default (nullable) -> rendered as a
      tri-state combobox: (Not Set) / Yes / No, same pattern used for
      IsWithinTolerance in CalibrationTestPoints_form
    - TechnicianID / SupervisorID are plain integers - the DDL declares no
      FOREIGN KEY for either, so they are not turned into FK comboboxes
    - pyodbc.IntegrityError caught separately for meaningful constraint messages
    - Dynamic FK-dependency check on delete using sys.foreign_keys (this
      matters here since FailureRecords.MaintenanceID references this table)
    - DowntimeDuration_Hours and TotalCost are computed columns (DATEDIFF /
      ISNULL sums) - excluded from the editable form and from INSERT/UPDATE
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, time as dtime

import pyodbc
from tkcalendar import DateEntry

from db_connection import get_connection


FK_LOOKUPS = {
    "InstrumentID": {
        "query": "SELECT InstrumentID, TagNumber, Description FROM Instruments ORDER BY TagNumber",
        "format": lambda r: f"{r[1]} - {r[2]}" if r[2] else r[1],
    },
}

TRISTATE_VALUES = ["(Not Set)", "Yes", "No"]

WORK_ORDER_TYPES = ["PM", "CM", "Breakdown", "Overhaul", "Modification"]
MAINTENANCE_TYPES = ["Preventive", "Corrective", "Predictive", "Breakdown"]
MAINTENANCE_CATEGORIES = ["Inspection", "Lubrication", "Adjustment", "Repair", "Replacement"]
PRIORITY_VALUES = ["Routine", "Medium", "High", "Emergency", "Critical"]
ROOT_CAUSE_CATEGORIES = ["Design", "Installation", "Operation", "Maintenance"]
STATUS_VALUES = ["Requested", "Scheduled", "In Progress", "On Hold", "Completed", "Cancelled"]

FIELD_TABS = [
    ("Work Order & Scheduling", [
        ("InstrumentID", "Instrument *", "fk", "InstrumentID"),
        ("WorkOrderNumber", "Work Order Number", "text", None),
        ("WorkOrderType", "Work Order Type", "combo", WORK_ORDER_TYPES),
        ("ScheduledDate", "Scheduled Date", "date", None),
        ("RequestedDate", "Requested Date", "date", None),
        ("StartDate", "Start Date/Time", "datetime", None),
        ("CompletionDate", "Completion Date/Time", "datetime", None),
    ]),
    ("Classification & Personnel", [
        ("MaintenanceType", "Maintenance Type", "combo", MAINTENANCE_TYPES),
        ("MaintenanceCategory", "Maintenance Category", "combo", MAINTENANCE_CATEGORIES),
        ("Priority", "Priority", "combo", PRIORITY_VALUES),
        ("RequestedBy", "Requested By", "text", None),
        ("AssignedTo", "Assigned To", "text", None),
        ("TechnicianID", "Technician ID", "int", None),
        ("SupervisorID", "Supervisor ID", "int", None),
        ("ContractorName", "Contractor Name", "text", None),
    ]),
    ("Problem & Root Cause", [
        ("ProblemDescription", "Problem Description", "multiline", None),
        ("SymptomObserved", "Symptom Observed", "multiline", None),
        ("RootCause", "Root Cause", "multiline", None),
        ("RootCauseCategory", "Root Cause Category", "combo", ROOT_CAUSE_CATEGORIES),
        ("FailureMode", "Failure Mode", "text", None),
    ]),
    ("Work Performed", [
        ("WorkPerformed", "Work Performed", "multiline", None),
        ("ActionTaken", "Action Taken", "multiline", None),
        ("PartsReplaced", "Parts Replaced", "multiline", None),
    ]),
    ("Testing", [
        ("TestingPerformed", "Testing Performed", "multiline", None),
        ("TestResults", "Test Results", "multiline", None),
        ("CalibrationPerformed", "Calibration Performed", "bit", None),
        ("FunctionalTestPassed", "Functional Test Passed", "bit", None),
    ]),
    ("Downtime", [
        ("DowntimeStart", "Downtime Start", "datetime", None),
        ("DowntimeEnd", "Downtime End", "datetime", None),
        ("PlannedDowntime", "Planned Downtime", "bit", None),
        ("ProductionImpact", "Production Impact", "text", None),
    ]),
    ("Cost", [
        ("LaborHours", "Labor Hours", "decimal", None),
        ("LaborCost", "Labor Cost", "decimal", None),
        ("PartsCost", "Parts Cost", "decimal", None),
        ("ContractorCost", "Contractor Cost", "decimal", None),
        ("OtherCosts", "Other Costs", "decimal", None),
    ]),
    ("Warranty & Status", [
        ("IsWarrantyClaim", "Is Warranty Claim", "bit", None),
        ("WarrantyClaimNumber", "Warranty Claim Number", "text", None),
        ("WarrantyApproved", "Warranty Approved", "bit_tristate", None),
        ("Status", "Status", "combo", STATUS_VALUES),
    ]),
    ("Follow-Up & Recommendations", [
        ("RequiresFollowUp", "Requires Follow-Up", "bit", None),
        ("FollowUpDate", "Follow-Up Date", "date", None),
        ("FollowUpAction", "Follow-Up Action", "multiline", None),
        ("Recommendations", "Recommendations", "multiline", None),
        ("PreventiveActions", "Preventive Actions", "multiline", None),
    ]),
    ("Permits & Safety", [
        ("PermitRequired", "Permit Required", "bit", None),
        ("PermitNumber", "Permit Number", "text", None),
        ("HotWorkPermit", "Hot Work Permit", "bit", None),
        ("ConfinedSpacePermit", "Confined Space Permit", "bit", None),
    ]),
    ("Documentation & Notes", [
        ("AttachmentPath", "Attachment Path", "text", None),
        ("Notes", "Notes", "multiline", None),
    ]),
]

# Columns computed by SQL Server (never sent on INSERT/UPDATE, never editable)
COMPUTED_COLUMNS = {"DowntimeDuration_Hours", "TotalCost"}

# BIT columns that DEFAULT to 1 (checked) for new records; everything else
# defaults to unchecked / (Not Set)
DEFAULT_TRUE_BITS = {"FunctionalTestPassed", "PlannedDowntime"}


class MaintenanceRecordsForm(ttk.Frame):
    TABLE_NAME = "MaintenanceRecords"

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.selected_id = None
        self.fk_lookups = {key: {} for key in FK_LOOKUPS}
        self.field_widgets = {}

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

        ttk.Label(filter_frame, text="Instrument:").grid(row=0, column=0, sticky="w", padx=5, pady=4)
        self.instrument_filter_var = tk.StringVar()
        self.instrument_filter_combo = ttk.Combobox(
            filter_frame, textvariable=self.instrument_filter_var, state="readonly", width=32
        )
        self.instrument_filter_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=4)
        self.instrument_filter_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_data())

        ttk.Label(filter_frame, text="Status:").grid(row=0, column=2, sticky="w", padx=5, pady=4)
        self.status_filter_var = tk.StringVar(value="(All)")
        ttk.Combobox(
            filter_frame, textvariable=self.status_filter_var, state="readonly", width=18,
            values=["(All)"] + STATUS_VALUES
        ).grid(row=0, column=3, sticky="ew", padx=5, pady=4)
        self.status_filter_var.trace_add("write", lambda *a: self.refresh_data())

        ttk.Label(filter_frame, text="Work Order Type:").grid(row=1, column=0, sticky="w", padx=5, pady=4)
        self.type_filter_var = tk.StringVar(value="(All)")
        ttk.Combobox(
            filter_frame, textvariable=self.type_filter_var, state="readonly", width=18,
            values=["(All)"] + WORK_ORDER_TYPES
        ).grid(row=1, column=1, sticky="ew", padx=5, pady=4)
        self.type_filter_var.trace_add("write", lambda *a: self.refresh_data())

        ttk.Label(filter_frame, text="Keyword (Work Order #):").grid(
            row=1, column=2, sticky="w", padx=5, pady=4
        )
        self.search_text_var = tk.StringVar()
        search_entry = ttk.Entry(filter_frame, textvariable=self.search_text_var, width=22)
        search_entry.grid(row=1, column=3, sticky="ew", padx=5, pady=4)
        search_entry.bind("<KeyRelease>", lambda e: self.refresh_data())

        btn_frame = ttk.Frame(filter_frame)
        btn_frame.grid(row=2, column=0, columnspan=4, sticky="w", padx=5, pady=(0, 4))
        ttk.Button(btn_frame, text="Apply Filter", command=self.refresh_data).pack(side="left", padx=3)
        ttk.Button(btn_frame, text="Clear Filter", command=self._clear_filter).pack(side="left", padx=3)

        for col in range(4):
            filter_frame.columnconfigure(col, weight=1)

        # ---------------- Treeview ----------------
        tree_frame = ttk.Frame(self)
        tree_frame.pack(side="top", fill="both", expand=True, padx=8, pady=4)

        columns = ("MaintenanceID", "Instrument", "WorkOrderNumber", "WorkOrderType",
                   "MaintenanceType", "Status", "CompletionDate")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=9)
        headings = {
            "MaintenanceID": "ID", "Instrument": "Instrument", "WorkOrderNumber": "Work Order #",
            "WorkOrderType": "WO Type", "MaintenanceType": "Maint. Type",
            "Status": "Status", "CompletionDate": "Completed",
        }
        widths = {
            "MaintenanceID": 50, "Instrument": 190, "WorkOrderNumber": 110,
            "WorkOrderType": 80, "MaintenanceType": 100, "Status": 90, "CompletionDate": 130,
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
        outer_panel = ttk.LabelFrame(self, text="Maintenance Record Details")
        outer_panel.pack(side="top", fill="both", expand=False, padx=8, pady=4)

        id_frame = ttk.Frame(outer_panel)
        id_frame.pack(side="top", fill="x", padx=5, pady=(5, 0))
        ttk.Label(id_frame, text="Maintenance ID:").pack(side="left", padx=(0, 5))
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
                var = tk.BooleanVar(value=(column in DEFAULT_TRUE_BITS))
                ttk.Checkbutton(tab_frame, variable=var).grid(
                    row=row, column=widget_col, sticky="w", padx=5, pady=4
                )
                self.field_widgets[column] = {"type": field_type, "var": var}

            elif field_type == "bit_tristate":
                var = tk.StringVar(value="(Not Set)")
                ttk.Combobox(
                    tab_frame, textvariable=var, state="readonly", width=24, values=TRISTATE_VALUES
                ).grid(row=row, column=widget_col, sticky="ew", padx=5, pady=4)
                self.field_widgets[column] = {"type": field_type, "var": var}

            elif field_type == "combo":
                var = tk.StringVar()
                ttk.Combobox(tab_frame, textvariable=var, width=24, values=extra).grid(
                    row=row, column=widget_col, sticky="ew", padx=5, pady=4
                )
                self.field_widgets[column] = {"type": field_type, "var": var}

            elif field_type == "fk":
                var = tk.StringVar()
                combo = ttk.Combobox(tab_frame, textvariable=var, state="readonly", width=30)
                combo.grid(row=row, column=widget_col, sticky="ew", padx=5, pady=4)
                self.field_widgets[column] = {"type": field_type, "var": var,
                                              "combo": combo, "lookup_key": extra}

            elif field_type == "date":
                set_var = tk.BooleanVar(value=False)
                wrapper = ttk.Frame(tab_frame)
                wrapper.grid(row=row, column=widget_col, sticky="w", padx=5, pady=4)
                entry = DateEntry(wrapper, width=13, date_pattern="yyyy-mm-dd", state="disabled")
                ttk.Checkbutton(
                    wrapper, text="Set", variable=set_var,
                    command=lambda e=entry, s=set_var: e.configure(
                        state="normal" if s.get() else "disabled"
                    )
                ).pack(side="left")
                entry.pack(side="left", padx=(5, 0))
                self.field_widgets[column] = {"type": field_type, "set_var": set_var, "entry": entry}

            elif field_type == "datetime":
                set_var = tk.BooleanVar(value=False)
                wrapper = ttk.Frame(tab_frame)
                wrapper.grid(row=row, column=widget_col, sticky="w", padx=5, pady=4)
                entry = DateEntry(wrapper, width=12, date_pattern="yyyy-mm-dd", state="disabled")
                time_var = tk.StringVar(value="00:00")
                time_entry = ttk.Entry(wrapper, textvariable=time_var, width=7, state="disabled")
                ttk.Checkbutton(
                    wrapper, text="Set", variable=set_var,
                    command=lambda e=entry, t=time_entry, s=set_var: (
                        e.configure(state="normal" if s.get() else "disabled"),
                        t.configure(state="normal" if s.get() else "disabled"),
                    )
                ).pack(side="left")
                entry.pack(side="left", padx=(5, 3))
                time_entry.pack(side="left")
                ttk.Label(wrapper, text="HH:MM", foreground="gray").pack(side="left", padx=(3, 0))
                self.field_widgets[column] = {
                    "type": field_type, "set_var": set_var, "entry": entry, "time_var": time_var
                }

            elif field_type == "multiline":
                text_frame = ttk.Frame(tab_frame)
                text_frame.grid(row=row, column=widget_col, columnspan=3, sticky="ew", padx=5, pady=4)
                text_widget = tk.Text(text_frame, height=3, width=50, wrap="word")
                scroll = ttk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
                text_widget.configure(yscrollcommand=scroll.set)
                text_widget.pack(side="left", fill="both", expand=True)
                scroll.pack(side="right", fill="y")
                self.field_widgets[column] = {"type": field_type, "widget": text_widget}
                row += 1
                col_pos = 0
                continue

            col_pos += 1
            if col_pos >= 2:
                col_pos = 0
                row += 1

    def _clear_filter(self):
        self.instrument_filter_var.set("(All)" if "(All)" in self.instrument_filter_combo["values"] else "")
        self.status_filter_var.set("(All)")
        self.type_filter_var.set("(All)")
        self.search_text_var.set("")
        self.refresh_data()

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

            self.instrument_filter_combo["values"] = ["(All)"] + list(
                self.fk_lookups.get("InstrumentID", {}).keys()
            )
            if not self.instrument_filter_var.get():
                self.instrument_filter_var.set("(All)")

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
                SELECT mr.MaintenanceID, i.TagNumber, i.Description, mr.WorkOrderNumber,
                       mr.WorkOrderType, mr.MaintenanceType, mr.Status, mr.CompletionDate
                FROM MaintenanceRecords mr
                LEFT JOIN Instruments i ON mr.InstrumentID = i.InstrumentID
                WHERE 1=1
            """
            params = []

            instrument_display = self.instrument_filter_var.get()
            if instrument_display and instrument_display != "(All)":
                instrument_id = self.fk_lookups.get("InstrumentID", {}).get(instrument_display)
                if instrument_id is not None:
                    query += " AND mr.InstrumentID = ?"
                    params.append(instrument_id)

            status_filter = self.status_filter_var.get()
            if status_filter and status_filter != "(All)":
                query += " AND mr.Status = ?"
                params.append(status_filter)

            type_filter = self.type_filter_var.get()
            if type_filter and type_filter != "(All)":
                query += " AND mr.WorkOrderType = ?"
                params.append(type_filter)

            keyword = self.search_text_var.get().strip()
            if keyword:
                query += " AND mr.WorkOrderNumber LIKE ?"
                params.append(f"%{keyword}%")

            query += " ORDER BY mr.CompletionDate DESC"

            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()

            for item in self.tree.get_children():
                self.tree.delete(item)

            for row in rows:
                (maintenance_id, tag_number, description, wo_number, wo_type,
                 maint_type, status, completion_date) = row
                instrument_label = f"{tag_number} - {description}" if description else (tag_number or "")
                self.tree.insert(
                    "", "end", iid=str(maintenance_id),
                    values=(
                        maintenance_id, instrument_label, wo_number or "", wo_type or "",
                        maint_type or "", status or "",
                        completion_date.strftime("%Y-%m-%d %H:%M") if completion_date else "",
                    )
                )

        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to load Maintenance Records data:\n{e}")
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

        maintenance_id = int(selection[0])
        columns = self._all_columns()
        try:
            conn = get_connection()
            cursor = conn.cursor()
            col_list = ", ".join(f"[{c}]" for c in columns)
            cursor.execute(
                f"SELECT MaintenanceID, {col_list} FROM MaintenanceRecords WHERE MaintenanceID = ?",
                (maintenance_id,)
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
                elif ftype == "bit_tristate":
                    if value is None:
                        widget_info["var"].set("(Not Set)")
                    else:
                        widget_info["var"].set("Yes" if value else "No")
                elif ftype == "date":
                    if value:
                        widget_info["set_var"].set(True)
                        widget_info["entry"].configure(state="normal")
                        widget_info["entry"].set_date(value)
                    else:
                        widget_info["set_var"].set(False)
                        widget_info["entry"].configure(state="disabled")
                elif ftype == "datetime":
                    if value:
                        widget_info["set_var"].set(True)
                        widget_info["entry"].configure(state="normal")
                        widget_info["entry"].set_date(value.date())
                        widget_info["time_var"].set(value.strftime("%H:%M"))
                    else:
                        widget_info["set_var"].set(False)
                        widget_info["entry"].configure(state="disabled")
                        widget_info["time_var"].set("00:00")
                elif ftype == "multiline":
                    widget_info["widget"].delete("1.0", tk.END)
                    if value:
                        widget_info["widget"].insert("1.0", value)
                else:  # int, decimal, text, combo
                    widget_info["var"].set("" if value is None else str(value))

        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to load Maintenance Record:\n{e}")
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
                widget_info["var"].set(column in DEFAULT_TRUE_BITS)
            elif ftype == "bit_tristate":
                widget_info["var"].set("(Not Set)")
            elif ftype == "date":
                widget_info["set_var"].set(False)
                widget_info["entry"].configure(state="disabled")
            elif ftype == "datetime":
                widget_info["set_var"].set(False)
                widget_info["entry"].configure(state="disabled")
                widget_info["time_var"].set("00:00")
            elif ftype == "multiline":
                widget_info["widget"].delete("1.0", tk.END)
            else:
                widget_info["var"].set("")

        self.tree.selection_remove(self.tree.selection())

    # ------------------------------------------------------------------
    # Save (Insert / Update)
    # ------------------------------------------------------------------
    def _parse_time_str(self, raw, label):
        raw = raw.strip()
        if not raw:
            return dtime(0, 0), True
        parts = raw.split(":")
        try:
            hour = int(parts[0])
            minute = int(parts[1]) if len(parts) > 1 else 0
            return dtime(hour, minute), True
        except (ValueError, IndexError):
            messagebox.showwarning("Validation", f"{label} time must be in HH:MM format.")
            return None, False

    def _collect_values(self):
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

                elif field_type == "bit_tristate":
                    tristate = widget_info["var"].get()
                    value = None if tristate == "(Not Set)" else (1 if tristate == "Yes" else 0)

                elif field_type == "date":
                    value = widget_info["entry"].get_date() if widget_info["set_var"].get() else None

                elif field_type == "datetime":
                    if widget_info["set_var"].get():
                        the_date = widget_info["entry"].get_date()
                        the_time, ok = self._parse_time_str(widget_info["time_var"].get(), label)
                        if not ok:
                            return None
                        value = datetime.combine(the_date, the_time)
                    else:
                        value = None

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
                    f"UPDATE MaintenanceRecords SET {set_clause} WHERE MaintenanceID = ?",
                    values + [self.selected_id]
                )
                conn.commit()
                messagebox.showinfo("Success", "Maintenance Record updated successfully.")
            else:
                col_list = ", ".join(f"[{c}]" for c in columns)
                placeholders = ", ".join("?" for _ in columns)
                cursor.execute(
                    f"INSERT INTO MaintenanceRecords ({col_list}) VALUES ({placeholders})",
                    values
                )
                conn.commit()
                messagebox.showinfo("Success", "Maintenance Record added successfully.")

            conn.close()
            self.refresh_data()
            self._new_record()

        except pyodbc.IntegrityError as e:
            messagebox.showerror(
                "Integrity Error",
                f"Save failed. This likely violates a unique constraint (Work Order Number "
                f"must be unique) or an invalid Instrument reference:\n{e}"
            )
        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to save Maintenance Record:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error while saving:\n{e}")

    # ------------------------------------------------------------------
    # Delete (with dynamic FK dependency check)
    # ------------------------------------------------------------------
    def _get_dependent_records(self, conn, maintenance_id):
        """
        Dynamically discover every table with a FK referencing MaintenanceRecords,
        then count rows that reference this MaintenanceID. This matters here
        since FailureRecords.MaintenanceID references this table.
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
                    (maintenance_id,)
                )
                count = count_cursor.fetchone()[0]
                if count > 0:
                    dependents.append((child_table, count))
            except pyodbc.Error:
                continue

        return dependents

    def _delete_record(self):
        if not self.selected_id:
            messagebox.showwarning("No Selection", "Please select a Maintenance Record to delete.")
            return

        try:
            conn = get_connection()
            dependents = self._get_dependent_records(conn, self.selected_id)

            if dependents:
                detail = "\n".join(f"  - {table}: {count} record(s)" for table, count in dependents)
                proceed = messagebox.askyesno(
                    "Maintenance Record In Use",
                    f"This Maintenance Record is referenced by other records:\n\n{detail}\n\n"
                    "Deleting it may fail or orphan related data depending on your "
                    "database's FK constraints.\n\nDo you still want to attempt deletion?"
                )
                if not proceed:
                    conn.close()
                    return
            else:
                confirm = messagebox.askyesno(
                    "Confirm Delete",
                    f"Delete this Maintenance Record (ID {self.selected_id})?"
                )
                if not confirm:
                    conn.close()
                    return

            cursor = conn.cursor()
            cursor.execute("DELETE FROM MaintenanceRecords WHERE MaintenanceID = ?", (self.selected_id,))
            conn.commit()
            conn.close()

            messagebox.showinfo("Deleted", "Maintenance Record deleted successfully.")
            self.refresh_data()
            self._new_record()

        except pyodbc.IntegrityError as e:
            messagebox.showerror(
                "Integrity Error",
                f"Cannot delete this Maintenance Record because other records depend on it "
                f"(e.g. a Failure Record referencing it):\n{e}"
            )
        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to delete Maintenance Record:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error while deleting:\n{e}")
