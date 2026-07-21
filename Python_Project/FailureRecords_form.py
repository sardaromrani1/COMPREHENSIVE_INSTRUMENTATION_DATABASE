"""
FailureRecords_form.py

CRUD form for the FailureRecords table.

This table has ~40 columns across failure details, classification, severity/
impact, response, resolution, repeat-failure analysis, cost, prevention, and
investigation - so, following the same approach used for Instruments_form and
CalibrationRecords_form, fields are declared once in FIELD_TABS and rendered
generically into a ttk.Notebook.

Conventions carried over from the rest of the project:
    - get_connection() from db_connection (pyodbc / ODBC Driver 17 / Windows Auth)
    - FK comboboxes:
        InstrumentID      -> Instruments (TagNumber - Description), required
        MaintenanceID     -> MaintenanceRecords (WorkOrderNumber - Type - date), optional
        PreviousFailureID -> FailureRecords itself (self-referencing), optional
    - FailureDate is DATETIME NOT NULL -> required Date + HH:MM fields
    - DetectedDate / ReportedDate / ResolutionDate are DATETIME, nullable ->
      "Set" checkbox + DateEntry + HH:MM
    - BIT columns rendered as checkbuttons
    - pyodbc.IntegrityError caught separately for meaningful constraint messages
    - Dynamic FK-dependency check on delete using sys.foreign_keys
    - MTTR_Hours and TotalCost are computed columns (DATEDIFF / ISNULL sums) -
      excluded from the editable form and from INSERT/UPDATE entirely
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, time as dtime

import pyodbc
from tkcalendar import DateEntry

from db_connection import get_connection


# ----------------------------------------------------------------------
# Field metadata (same field_type vocabulary as CalibrationRecords_form)
# ----------------------------------------------------------------------

FK_LOOKUPS = {
    "InstrumentID": {
        "query": "SELECT InstrumentID, TagNumber, Description FROM Instruments ORDER BY TagNumber",
        "format": lambda r: f"{r[1]} - {r[2]}" if r[2] else r[1],
    },
    "MaintenanceID": {
        "query": """
            SELECT MaintenanceID, WorkOrderNumber, MaintenanceType, CompletionDate
            FROM MaintenanceRecords
            ORDER BY CompletionDate DESC
        """,
        "format": lambda r: (
            f"{r[1] or ('WO #' + str(r[0]))} - {r[2] or 'Unknown Type'}"
            f" ({r[3].strftime('%Y-%m-%d') if r[3] else 'pending'})"
        ),
    },
    "PreviousFailureID": {
        "query": """
            SELECT fr.FailureID, i.TagNumber, fr.FailureDate, fr.FailureMode
            FROM FailureRecords fr
            LEFT JOIN Instruments i ON fr.InstrumentID = i.InstrumentID
            ORDER BY fr.FailureDate DESC
        """,
        "format": lambda r: (
            f"{r[1] or 'Unknown'} - {r[2].strftime('%Y-%m-%d') if r[2] else ''}"
            f" - {r[3] or ''} (#{r[0]})"
        ),
    },
}

FAILURE_TYPES = ["Mechanical", "Electrical", "Electronic", "Software", "Process"]
SEVERITY_VALUES = ["Minor", "Moderate", "Major", "Critical", "Catastrophic"]
DETECTION_METHODS = ["Operator Observation", "Alarm", "Inspection", "Calibration", "Maintenance"]

FIELD_TABS = [
    ("Failure Details & Personnel", [
        ("InstrumentID", "Instrument *", "fk", "InstrumentID"),
        ("MaintenanceID", "Related Maintenance Record", "fk", "MaintenanceID"),
        ("FailureDate", "Failure Date/Time *", "datetime_required", None),
        ("DetectedDate", "Detected Date/Time", "datetime", None),
        ("ReportedDate", "Reported Date/Time", "datetime", None),
        ("DetectedBy", "Detected By", "text", None),
        ("DetectionMethod", "Detection Method", "combo", DETECTION_METHODS),
    ]),
    ("Classification", [
        ("FailureMode", "Failure Mode", "text", None),
        ("FailureType", "Failure Type", "combo", FAILURE_TYPES),
        ("FailureMechanism", "Failure Mechanism", "text", None),
        ("FailureCause", "Failure Cause", "multiline", None),
        ("RootCause", "Root Cause", "multiline", None),
    ]),
    ("Severity & Impact", [
        ("Severity", "Severity", "combo", SEVERITY_VALUES),
        ("SafetyImpact", "Safety Impact", "multiline", None),
        ("ProductionImpact", "Production Impact", "multiline", None),
        ("EnvironmentalImpact", "Environmental Impact", "multiline", None),
        ("FinancialImpact", "Financial Impact", "decimal", None),
    ]),
    ("Response", [
        ("ImmediateAction", "Immediate Action", "multiline", None),
        ("BypassImplemented", "Bypass Implemented", "bit", None),
        ("RedundantInstrumentActivated", "Redundant Instrument Activated", "bit", None),
        ("EmergencyShutdownTriggered", "Emergency Shutdown Triggered", "bit", None),
    ]),
    ("Resolution & Repeat Analysis", [
        ("ResolutionDate", "Resolution Date/Time", "datetime", None),
        ("ResolutionDescription", "Resolution Description", "multiline", None),
        ("IsRepeatFailure", "Is Repeat Failure", "bit", None),
        ("PreviousFailureID", "Previous Failure", "fk", "PreviousFailureID"),
        ("RepeatFailureCount", "Repeat Failure Count", "int", None),
        ("TimeSincePreviousFailure_Days", "Time Since Previous Failure (days)", "int", None),
    ]),
    ("Cost", [
        ("RepairCost", "Repair Cost", "decimal", None),
        ("ProductionLossCost", "Production Loss Cost", "decimal", None),
    ]),
    ("Prevention & Investigation", [
        ("PreventiveAction", "Preventive Action", "multiline", None),
        ("DesignModificationRequired", "Design Modification Required", "bit", None),
        ("ProcedureUpdateRequired", "Procedure Update Required", "bit", None),
        ("TrainingRequired", "Training Required", "bit", None),
        ("InvestigationRequired", "Investigation Required", "bit", None),
        ("InvestigationCompleted", "Investigation Completed", "bit", None),
        ("InvestigationReport", "Investigation Report (Path)", "text", None),
    ]),
    ("Notes", [
        ("Notes", "Notes", "multiline", None),
    ]),
]

# Columns computed by SQL Server (never sent on INSERT/UPDATE, never editable)
COMPUTED_COLUMNS = {"MTTR_Hours", "TotalCost"}


class FailureRecordsForm(ttk.Frame):
    TABLE_NAME = "FailureRecords"

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

        ttk.Label(filter_frame, text="Severity:").grid(row=0, column=2, sticky="w", padx=5, pady=4)
        self.severity_filter_var = tk.StringVar(value="(All)")
        ttk.Combobox(
            filter_frame, textvariable=self.severity_filter_var, state="readonly", width=18,
            values=["(All)"] + SEVERITY_VALUES
        ).grid(row=0, column=3, sticky="ew", padx=5, pady=4)
        self.severity_filter_var.trace_add("write", lambda *a: self.refresh_data())

        ttk.Label(filter_frame, text="Failure Date From:").grid(row=1, column=0, sticky="w", padx=5, pady=4)
        self.date_from = DateEntry(filter_frame, width=12, date_pattern="yyyy-mm-dd")
        self.date_from.grid(row=1, column=1, sticky="w", padx=5, pady=4)
        self.date_from_enabled = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            filter_frame, text="Use", variable=self.date_from_enabled, command=self.refresh_data
        ).grid(row=1, column=1, sticky="e", padx=5, pady=4)

        ttk.Label(filter_frame, text="Failure Date To:").grid(row=1, column=2, sticky="w", padx=5, pady=4)
        self.date_to = DateEntry(filter_frame, width=12, date_pattern="yyyy-mm-dd")
        self.date_to.grid(row=1, column=3, sticky="w", padx=5, pady=4)
        self.date_to_enabled = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            filter_frame, text="Use", variable=self.date_to_enabled, command=self.refresh_data
        ).grid(row=1, column=3, sticky="e", padx=5, pady=4)

        btn_frame = ttk.Frame(filter_frame)
        btn_frame.grid(row=2, column=0, columnspan=4, sticky="w", padx=5, pady=(0, 4))
        ttk.Button(btn_frame, text="Apply Filter", command=self.refresh_data).pack(side="left", padx=3)
        ttk.Button(btn_frame, text="Clear Filter", command=self._clear_filter).pack(side="left", padx=3)

        for col in range(4):
            filter_frame.columnconfigure(col, weight=1)

        # ---------------- Treeview ----------------
        tree_frame = ttk.Frame(self)
        tree_frame.pack(side="top", fill="both", expand=True, padx=8, pady=4)

        columns = ("FailureID", "Instrument", "FailureDate", "FailureMode",
                   "Severity", "IsRepeatFailure")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=9)
        headings = {
            "FailureID": "ID", "Instrument": "Instrument", "FailureDate": "Failure Date",
            "FailureMode": "Failure Mode", "Severity": "Severity", "IsRepeatFailure": "Repeat?",
        }
        widths = {
            "FailureID": 50, "Instrument": 200, "FailureDate": 130,
            "FailureMode": 160, "Severity": 90, "IsRepeatFailure": 70,
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
        outer_panel = ttk.LabelFrame(self, text="Failure Record Details")
        outer_panel.pack(side="top", fill="both", expand=False, padx=8, pady=4)

        id_frame = ttk.Frame(outer_panel)
        id_frame.pack(side="top", fill="x", padx=5, pady=(5, 0))
        ttk.Label(id_frame, text="Failure ID:").pack(side="left", padx=(0, 5))
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

            if field_type in ("text",):
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

            elif field_type == "date_required":
                entry = DateEntry(tab_frame, width=15, date_pattern="yyyy-mm-dd")
                entry.grid(row=row, column=widget_col, sticky="w", padx=5, pady=4)
                self.field_widgets[column] = {"type": field_type, "entry": entry}

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

            elif field_type == "datetime_required":
                wrapper = ttk.Frame(tab_frame)
                wrapper.grid(row=row, column=widget_col, sticky="w", padx=5, pady=4)
                entry = DateEntry(wrapper, width=12, date_pattern="yyyy-mm-dd")
                time_var = tk.StringVar(value="00:00")
                time_entry = ttk.Entry(wrapper, textvariable=time_var, width=7)
                entry.pack(side="left", padx=(0, 3))
                time_entry.pack(side="left")
                ttk.Label(wrapper, text="HH:MM", foreground="gray").pack(side="left", padx=(3, 0))
                self.field_widgets[column] = {"type": field_type, "entry": entry, "time_var": time_var}

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
        self.severity_filter_var.set("(All)")
        self.date_from_enabled.set(False)
        self.date_to_enabled.set(False)
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
                    # Skip the record currently being edited when populating
                    # PreviousFailureID, so a failure can't reference itself.
                    if key == "PreviousFailureID" and self.selected_id and r[0] == self.selected_id:
                        continue
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
                SELECT fr.FailureID, i.TagNumber, i.Description, fr.FailureDate,
                       fr.FailureMode, fr.Severity, fr.IsRepeatFailure
                FROM FailureRecords fr
                LEFT JOIN Instruments i ON fr.InstrumentID = i.InstrumentID
                WHERE 1=1
            """
            params = []

            instrument_display = self.instrument_filter_var.get()
            if instrument_display and instrument_display != "(All)":
                instrument_id = self.fk_lookups.get("InstrumentID", {}).get(instrument_display)
                if instrument_id is not None:
                    query += " AND fr.InstrumentID = ?"
                    params.append(instrument_id)

            severity_filter = self.severity_filter_var.get()
            if severity_filter and severity_filter != "(All)":
                query += " AND fr.Severity = ?"
                params.append(severity_filter)

            if self.date_from_enabled.get():
                query += " AND fr.FailureDate >= ?"
                params.append(self.date_from.get_date())

            if self.date_to_enabled.get():
                query += " AND fr.FailureDate <= ?"
                params.append(self.date_to.get_date())

            query += " ORDER BY fr.FailureDate DESC"

            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()

            for item in self.tree.get_children():
                self.tree.delete(item)

            for row in rows:
                (failure_id, tag_number, description, failure_date, failure_mode,
                 severity, is_repeat) = row
                instrument_label = f"{tag_number} - {description}" if description else (tag_number or "")
                self.tree.insert(
                    "", "end", iid=str(failure_id),
                    values=(
                        failure_id, instrument_label,
                        failure_date.strftime("%Y-%m-%d %H:%M") if failure_date else "",
                        failure_mode or "", severity or "",
                        "Yes" if is_repeat else "No",
                    )
                )

        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to load Failure Records data:\n{e}")
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

        failure_id = int(selection[0])
        columns = self._all_columns()
        try:
            conn = get_connection()
            cursor = conn.cursor()
            col_list = ", ".join(f"[{c}]" for c in columns)
            cursor.execute(
                f"SELECT FailureID, {col_list} FROM FailureRecords WHERE FailureID = ?",
                (failure_id,)
            )
            row = cursor.fetchone()
            conn.close()

            if not row:
                return

            self.selected_id = row[0]
            self.id_var.set(str(row[0]))

            # Reload PreviousFailureID lookup now that we know which record is
            # selected, so this record can't be offered as its own predecessor.
            self._load_all_fk_lookups()

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
                elif ftype == "date_required":
                    if value:
                        widget_info["entry"].set_date(value)
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
                elif ftype == "datetime_required":
                    if value:
                        widget_info["entry"].set_date(value.date())
                        widget_info["time_var"].set(value.strftime("%H:%M"))
                elif ftype == "multiline":
                    widget_info["widget"].delete("1.0", tk.END)
                    if value:
                        widget_info["widget"].insert("1.0", value)
                else:  # int, decimal, text, combo
                    widget_info["var"].set("" if value is None else str(value))

        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to load Failure Record:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error while loading record:\n{e}")

    def _new_record(self):
        self.selected_id = None
        self.id_var.set("")
        self._load_all_fk_lookups()   # restores the full PreviousFailureID list

        for column, widget_info in self.field_widgets.items():
            ftype = widget_info["type"]
            if ftype == "fk":
                widget_info["var"].set("")
            elif ftype == "bit":
                widget_info["var"].set(False)
            elif ftype == "date":
                widget_info["set_var"].set(False)
                widget_info["entry"].configure(state="disabled")
            elif ftype == "date_required":
                widget_info["entry"].set_date(datetime.now())
            elif ftype == "datetime":
                widget_info["set_var"].set(False)
                widget_info["entry"].configure(state="disabled")
                widget_info["time_var"].set("00:00")
            elif ftype == "datetime_required":
                widget_info["entry"].set_date(datetime.now())
                widget_info["time_var"].set(datetime.now().strftime("%H:%M"))
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

                elif field_type == "date":
                    value = widget_info["entry"].get_date() if widget_info["set_var"].get() else None

                elif field_type == "date_required":
                    value = widget_info["entry"].get_date()

                elif field_type == "datetime":
                    if widget_info["set_var"].get():
                        the_date = widget_info["entry"].get_date()
                        the_time, ok = self._parse_time_str(widget_info["time_var"].get(), label)
                        if not ok:
                            return None
                        value = datetime.combine(the_date, the_time)
                    else:
                        value = None

                elif field_type == "datetime_required":
                    the_date = widget_info["entry"].get_date()
                    the_time, ok = self._parse_time_str(widget_info["time_var"].get(), label)
                    if not ok:
                        return None
                    value = datetime.combine(the_date, the_time)

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
                    f"UPDATE FailureRecords SET {set_clause} WHERE FailureID = ?",
                    values + [self.selected_id]
                )
                conn.commit()
                messagebox.showinfo("Success", "Failure Record updated successfully.")
            else:
                col_list = ", ".join(f"[{c}]" for c in columns)
                placeholders = ", ".join("?" for _ in columns)
                cursor.execute(
                    f"INSERT INTO FailureRecords ({col_list}) VALUES ({placeholders})",
                    values
                )
                conn.commit()
                messagebox.showinfo("Success", "Failure Record added successfully.")

            conn.close()
            self.refresh_data()
            self._new_record()

        except pyodbc.IntegrityError as e:
            messagebox.showerror(
                "Integrity Error",
                f"Save failed. This likely indicates an invalid Instrument, Maintenance "
                f"Record, or Previous Failure reference:\n{e}"
            )
        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to save Failure Record:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error while saving:\n{e}")

    # ------------------------------------------------------------------
    # Delete (with dynamic FK dependency check)
    # ------------------------------------------------------------------
    def _get_dependent_records(self, conn, failure_id):
        """
        Dynamically discover every table with a FK referencing FailureRecords,
        then count rows that reference this FailureID. This includes
        FailureRecords itself, via the self-referencing PreviousFailureID FK.
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
                    (failure_id,)
                )
                count = count_cursor.fetchone()[0]
                if count > 0:
                    dependents.append((child_table, count))
            except pyodbc.Error:
                continue

        return dependents

    def _delete_record(self):
        if not self.selected_id:
            messagebox.showwarning("No Selection", "Please select a Failure Record to delete.")
            return

        try:
            conn = get_connection()
            dependents = self._get_dependent_records(conn, self.selected_id)

            if dependents:
                detail = "\n".join(f"  - {table}: {count} record(s)" for table, count in dependents)
                proceed = messagebox.askyesno(
                    "Failure Record In Use",
                    f"This Failure Record is referenced by other records:\n\n{detail}\n\n"
                    "Deleting it may fail or orphan related data depending on your "
                    "database's FK constraints.\n\nDo you still want to attempt deletion?"
                )
                if not proceed:
                    conn.close()
                    return
            else:
                confirm = messagebox.askyesno(
                    "Confirm Delete",
                    f"Delete this Failure Record (ID {self.selected_id})?"
                )
                if not confirm:
                    conn.close()
                    return

            cursor = conn.cursor()
            cursor.execute("DELETE FROM FailureRecords WHERE FailureID = ?", (self.selected_id,))
            conn.commit()
            conn.close()

            messagebox.showinfo("Deleted", "Failure Record deleted successfully.")
            self.refresh_data()
            self._new_record()

        except pyodbc.IntegrityError as e:
            messagebox.showerror(
                "Integrity Error",
                f"Cannot delete this Failure Record because other records depend on it "
                f"(this may include another Failure Record referencing it as its Previous "
                f"Failure):\n{e}"
            )
        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to delete Failure Record:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error while deleting:\n{e}")
