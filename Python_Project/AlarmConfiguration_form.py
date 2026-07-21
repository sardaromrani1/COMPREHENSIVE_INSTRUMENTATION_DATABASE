"""
AlarmConfiguration_form.py

CRUD form for the AlarmConfiguration table.

    CREATE TABLE AlarmConfiguration (
        AlarmID INT PRIMARY KEY IDENTITY(1,1),
        InstrumentID INT NOT NULL,
        AlarmType NVARCHAR(50),
        AlarmDescription NVARCHAR(200),
        AlarmSetpoint DECIMAL(18,4),
        AlarmDeadband DECIMAL(18,4),
        AlarmDelay_Seconds INT,
        AlarmPriority NVARCHAR(20),
        AlarmAction NVARCHAR(500),
        RequiresAcknowledgement BIT DEFAULT 1,
        IsEnabled BIT DEFAULT 1,
        EnabledDate DATE,
        DisabledDate DATE,
        DisabledBy NVARCHAR(100),
        DisabledReason NVARCHAR(500),
        FOREIGN KEY (InstrumentID) REFERENCES Instruments(InstrumentID)
    );

Follows the same conventions as the other forms in this project:
    - get_connection() from db_connection (pyodbc / ODBC Driver 17 / Windows Auth)
    - FK combobox (InstrumentID -> Instruments) showing TagNumber - Description,
      storing the integer ID
    - Nullable dates (EnabledDate, DisabledDate) via "Set" checkbox + DateEntry
    - BIT columns (RequiresAcknowledgement, IsEnabled) rendered as checkbuttons
    - pyodbc.IntegrityError caught separately for meaningful constraint messages
    - Dynamic FK-dependency check on delete using sys.foreign_keys
    - Column-scoped search / filter panel with live keyword filtering
"""

import tkinter as tk
from tkinter import ttk, messagebox

import pyodbc
from tkcalendar import DateEntry

from db_connection import get_connection


ALARM_TYPES = ["HH", "H", "L", "LL", "Deviation", "Rate of Change"]
ALARM_PRIORITIES = ["Low", "Medium", "High", "Critical", "Emergency"]


class AlarmConfigurationForm(ttk.Frame):
    TABLE_NAME = "AlarmConfiguration"

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.selected_id = None
        self.instrument_lookup = {}   # display string -> InstrumentID

        self._build_ui()
        self._load_instrument_lookup()
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

        ttk.Label(filter_frame, text="Alarm Type:").grid(row=0, column=2, sticky="w", padx=5, pady=4)
        self.type_filter_var = tk.StringVar(value="(All)")
        self.type_filter_combo = ttk.Combobox(
            filter_frame, textvariable=self.type_filter_var, state="readonly", width=18,
            values=["(All)"] + ALARM_TYPES
        )
        self.type_filter_combo.grid(row=0, column=3, sticky="ew", padx=5, pady=4)
        self.type_filter_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_data())

        ttk.Label(filter_frame, text="Priority:").grid(row=1, column=0, sticky="w", padx=5, pady=4)
        self.priority_filter_var = tk.StringVar(value="(All)")
        self.priority_filter_combo = ttk.Combobox(
            filter_frame, textvariable=self.priority_filter_var, state="readonly", width=18,
            values=["(All)"] + ALARM_PRIORITIES
        )
        self.priority_filter_combo.grid(row=1, column=1, sticky="ew", padx=5, pady=4)
        self.priority_filter_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_data())

        ttk.Label(filter_frame, text="Enabled:").grid(row=1, column=2, sticky="w", padx=5, pady=4)
        self.enabled_filter_var = tk.StringVar(value="(All)")
        self.enabled_filter_combo = ttk.Combobox(
            filter_frame, textvariable=self.enabled_filter_var, state="readonly", width=18,
            values=["(All)", "Yes", "No"]
        )
        self.enabled_filter_combo.grid(row=1, column=3, sticky="ew", padx=5, pady=4)
        self.enabled_filter_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_data())

        btn_frame = ttk.Frame(filter_frame)
        btn_frame.grid(row=2, column=0, columnspan=4, sticky="w", padx=5, pady=(0, 4))
        ttk.Button(btn_frame, text="Apply Filter", command=self.refresh_data).pack(side="left", padx=3)
        ttk.Button(btn_frame, text="Clear Filter", command=self._clear_filter).pack(side="left", padx=3)

        for col in range(4):
            filter_frame.columnconfigure(col, weight=1)

        # ---------------- Treeview ----------------
        tree_frame = ttk.Frame(self)
        tree_frame.pack(side="top", fill="both", expand=True, padx=8, pady=4)

        columns = ("AlarmID", "Instrument", "AlarmType", "AlarmSetpoint",
                   "AlarmPriority", "IsEnabled")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=10)
        headings = {
            "AlarmID": "ID", "Instrument": "Instrument", "AlarmType": "Type",
            "AlarmSetpoint": "Setpoint", "AlarmPriority": "Priority", "IsEnabled": "Enabled",
        }
        widths = {
            "AlarmID": 50, "Instrument": 220, "AlarmType": 90,
            "AlarmSetpoint": 90, "AlarmPriority": 90, "IsEnabled": 70,
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

        # ---------------- Entry panel ----------------
        panel = ttk.LabelFrame(self, text="Alarm Configuration Details")
        panel.pack(side="top", fill="x", padx=8, pady=4)
        for col in range(4):
            panel.columnconfigure(col, weight=1)

        # AlarmID (disabled, identity)
        ttk.Label(panel, text="Alarm ID:").grid(row=0, column=0, sticky="w", padx=5, pady=4)
        self.id_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.id_var, width=20, state="disabled").grid(
            row=0, column=1, sticky="ew", padx=5, pady=4
        )

        # Instrument (FK combobox, required)
        ttk.Label(panel, text="Instrument *:").grid(row=0, column=2, sticky="w", padx=5, pady=4)
        self.instrument_var = tk.StringVar()
        self.instrument_combo = ttk.Combobox(
            panel, textvariable=self.instrument_var, state="readonly", width=32
        )
        self.instrument_combo.grid(row=0, column=3, sticky="ew", padx=5, pady=4)

        # AlarmType
        ttk.Label(panel, text="Alarm Type:").grid(row=1, column=0, sticky="w", padx=5, pady=4)
        self.alarm_type_var = tk.StringVar()
        self.alarm_type_combo = ttk.Combobox(
            panel, textvariable=self.alarm_type_var, width=18, values=ALARM_TYPES
        )
        self.alarm_type_combo.grid(row=1, column=1, sticky="ew", padx=5, pady=4)

        # AlarmPriority
        ttk.Label(panel, text="Alarm Priority:").grid(row=1, column=2, sticky="w", padx=5, pady=4)
        self.alarm_priority_var = tk.StringVar()
        self.alarm_priority_combo = ttk.Combobox(
            panel, textvariable=self.alarm_priority_var, width=26, values=ALARM_PRIORITIES
        )
        self.alarm_priority_combo.grid(row=1, column=3, sticky="ew", padx=5, pady=4)

        # AlarmDescription
        ttk.Label(panel, text="Alarm Description:").grid(row=2, column=0, sticky="w", padx=5, pady=4)
        self.alarm_description_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.alarm_description_var, width=20).grid(
            row=2, column=1, sticky="ew", padx=5, pady=4
        )

        # AlarmSetpoint
        ttk.Label(panel, text="Alarm Setpoint:").grid(row=2, column=2, sticky="w", padx=5, pady=4)
        self.alarm_setpoint_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.alarm_setpoint_var, width=26).grid(
            row=2, column=3, sticky="ew", padx=5, pady=4
        )

        # AlarmDeadband
        ttk.Label(panel, text="Alarm Deadband:").grid(row=3, column=0, sticky="w", padx=5, pady=4)
        self.alarm_deadband_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.alarm_deadband_var, width=20).grid(
            row=3, column=1, sticky="ew", padx=5, pady=4
        )

        # AlarmDelay_Seconds
        ttk.Label(panel, text="Alarm Delay (seconds):").grid(row=3, column=2, sticky="w", padx=5, pady=4)
        self.alarm_delay_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.alarm_delay_var, width=26).grid(
            row=3, column=3, sticky="ew", padx=5, pady=4
        )

        # RequiresAcknowledgement / IsEnabled (bits)
        check_frame = ttk.Frame(panel)
        check_frame.grid(row=4, column=0, columnspan=4, sticky="w", padx=5, pady=4)

        self.requires_ack_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            check_frame, text="Requires Acknowledgement", variable=self.requires_ack_var
        ).pack(side="left", padx=(0, 15))

        self.is_enabled_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            check_frame, text="Is Enabled", variable=self.is_enabled_var
        ).pack(side="left")

        # ---- Nullable dates: EnabledDate, DisabledDate ----
        date_frame = ttk.LabelFrame(panel, text="Dates")
        date_frame.grid(row=5, column=0, columnspan=4, sticky="ew", padx=5, pady=(8, 4))
        for col in range(4):
            date_frame.columnconfigure(col, weight=1)

        self.enabled_date_set_var = tk.BooleanVar(value=False)
        self.enabled_date_entry = self._make_date_field(
            date_frame, "Enabled Date:", self.enabled_date_set_var, row=0, col=0
        )

        self.disabled_date_set_var = tk.BooleanVar(value=False)
        self.disabled_date_entry = self._make_date_field(
            date_frame, "Disabled Date:", self.disabled_date_set_var, row=0, col=2
        )

        # DisabledBy
        ttk.Label(panel, text="Disabled By:").grid(row=6, column=0, sticky="w", padx=5, pady=4)
        self.disabled_by_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.disabled_by_var, width=20).grid(
            row=6, column=1, sticky="ew", padx=5, pady=4
        )

        # AlarmAction (multi-line, 500 chars)
        ttk.Label(panel, text="Alarm Action:").grid(row=7, column=0, sticky="nw", padx=5, pady=4)
        action_frame = ttk.Frame(panel)
        action_frame.grid(row=7, column=1, columnspan=3, sticky="ew", padx=5, pady=4)
        self.alarm_action_text = tk.Text(action_frame, height=3, width=50, wrap="word")
        action_scroll = ttk.Scrollbar(action_frame, orient="vertical", command=self.alarm_action_text.yview)
        self.alarm_action_text.configure(yscrollcommand=action_scroll.set)
        self.alarm_action_text.pack(side="left", fill="both", expand=True)
        action_scroll.pack(side="right", fill="y")

        # DisabledReason (multi-line, 500 chars)
        ttk.Label(panel, text="Disabled Reason:").grid(row=8, column=0, sticky="nw", padx=5, pady=4)
        reason_frame = ttk.Frame(panel)
        reason_frame.grid(row=8, column=1, columnspan=3, sticky="ew", padx=5, pady=4)
        self.disabled_reason_text = tk.Text(reason_frame, height=3, width=50, wrap="word")
        reason_scroll = ttk.Scrollbar(
            reason_frame, orient="vertical", command=self.disabled_reason_text.yview
        )
        self.disabled_reason_text.configure(yscrollcommand=reason_scroll.set)
        self.disabled_reason_text.pack(side="left", fill="both", expand=True)
        reason_scroll.pack(side="right", fill="y")

        ttk.Label(panel, text="* Required fields", foreground="gray").grid(
            row=9, column=0, columnspan=2, sticky="w", padx=5, pady=4
        )

        # Action buttons
        action_buttons_frame = ttk.Frame(panel)
        action_buttons_frame.grid(row=10, column=0, columnspan=4, sticky="e", padx=5, pady=(10, 5))
        ttk.Button(action_buttons_frame, text="New", command=self._new_record).pack(side="left", padx=3)
        ttk.Button(action_buttons_frame, text="Save", command=self._save_record).pack(side="left", padx=3)
        ttk.Button(action_buttons_frame, text="Delete", command=self._delete_record).pack(side="left", padx=3)
        ttk.Button(action_buttons_frame, text="Refresh", command=self.refresh_data).pack(side="left", padx=3)
        ttk.Button(
            action_buttons_frame, text="Reload Instruments", command=self._load_instrument_lookup
        ).pack(side="left", padx=3)

    def _make_date_field(self, parent, label, set_var, row, col):
        ttk.Label(parent, text=label).grid(row=row, column=col, sticky="w", padx=5, pady=4)
        wrapper = ttk.Frame(parent)
        wrapper.grid(row=row, column=col + 1, sticky="w", padx=5, pady=4)
        entry = DateEntry(wrapper, width=13, date_pattern="yyyy-mm-dd", state="disabled")
        ttk.Checkbutton(
            wrapper, text="Set", variable=set_var,
            command=lambda: entry.configure(state="normal" if set_var.get() else "disabled")
        ).pack(side="left")
        entry.pack(side="left", padx=(5, 0))
        return entry

    def _clear_filter(self):
        self.instrument_filter_var.set("(All)" if "(All)" in self.instrument_filter_combo["values"] else "")
        self.type_filter_combo.set("(All)")
        self.priority_filter_combo.set("(All)")
        self.enabled_filter_combo.set("(All)")
        self.refresh_data()

    # ------------------------------------------------------------------
    # Instrument FK lookup
    # ------------------------------------------------------------------
    def _load_instrument_lookup(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT InstrumentID, TagNumber, Description
                FROM Instruments
                ORDER BY TagNumber
                """
            )
            rows = cursor.fetchall()
            conn.close()

            self.instrument_lookup = {}
            display_values = []
            for instrument_id, tag_number, description in rows:
                display = f"{tag_number} - {description}" if description else tag_number
                self.instrument_lookup[display] = instrument_id
                display_values.append(display)

            self.instrument_combo["values"] = display_values
            self.instrument_filter_combo["values"] = ["(All)"] + display_values
            if not self.instrument_filter_var.get():
                self.instrument_filter_var.set("(All)")

        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to load Instruments lookup:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error while loading Instruments:\n{e}")

    def _instrument_display_for_id(self, instrument_id):
        for display, iid in self.instrument_lookup.items():
            if iid == instrument_id:
                return display
        return f"[ID {instrument_id}]"

    # ------------------------------------------------------------------
    # Data loading / search
    # ------------------------------------------------------------------
    def refresh_data(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()

            query = """
                SELECT ac.AlarmID, ac.InstrumentID, i.TagNumber, i.Description,
                       ac.AlarmType, ac.AlarmSetpoint, ac.AlarmPriority, ac.IsEnabled
                FROM AlarmConfiguration ac
                LEFT JOIN Instruments i ON ac.InstrumentID = i.InstrumentID
                WHERE 1=1
            """
            params = []

            instrument_display = self.instrument_filter_var.get()
            if instrument_display and instrument_display != "(All)":
                instrument_id = self.instrument_lookup.get(instrument_display)
                if instrument_id is not None:
                    query += " AND ac.InstrumentID = ?"
                    params.append(instrument_id)

            type_filter = self.type_filter_var.get()
            if type_filter and type_filter != "(All)":
                query += " AND ac.AlarmType = ?"
                params.append(type_filter)

            priority_filter = self.priority_filter_var.get()
            if priority_filter and priority_filter != "(All)":
                query += " AND ac.AlarmPriority = ?"
                params.append(priority_filter)

            enabled_filter = self.enabled_filter_var.get()
            if enabled_filter and enabled_filter != "(All)":
                query += " AND ac.IsEnabled = ?"
                params.append(1 if enabled_filter == "Yes" else 0)

            query += " ORDER BY i.TagNumber, ac.AlarmType"

            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()

            for item in self.tree.get_children():
                self.tree.delete(item)

            for row in rows:
                (alarm_id, instrument_id, tag_number, description,
                 alarm_type, setpoint, priority, is_enabled) = row
                instrument_label = f"{tag_number} - {description}" if description else (tag_number or "")
                self.tree.insert(
                    "", "end", iid=str(alarm_id),
                    values=(
                        alarm_id, instrument_label, alarm_type or "",
                        setpoint if setpoint is not None else "",
                        priority or "", "Yes" if is_enabled else "No",
                    )
                )

        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to load Alarm Configuration data:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error while loading data:\n{e}")

    # ------------------------------------------------------------------
    # Selection / form population
    # ------------------------------------------------------------------
    def _on_select(self, event):
        selection = self.tree.selection()
        if not selection:
            return

        alarm_id = int(selection[0])
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT AlarmID, InstrumentID, AlarmType, AlarmDescription, AlarmSetpoint,
                       AlarmDeadband, AlarmDelay_Seconds, AlarmPriority, AlarmAction,
                       RequiresAcknowledgement, IsEnabled, EnabledDate, DisabledDate,
                       DisabledBy, DisabledReason
                FROM AlarmConfiguration
                WHERE AlarmID = ?
                """,
                (alarm_id,)
            )
            row = cursor.fetchone()
            conn.close()

            if not row:
                return

            (aid, instrument_id, alarm_type, alarm_description, setpoint, deadband,
             delay_seconds, priority, alarm_action, requires_ack, is_enabled,
             enabled_date, disabled_date, disabled_by, disabled_reason) = row

            self.selected_id = aid
            self.id_var.set(str(aid))
            self.instrument_var.set(self._instrument_display_for_id(instrument_id))
            self.alarm_type_var.set(alarm_type or "")
            self.alarm_priority_var.set(priority or "")
            self.alarm_description_var.set(alarm_description or "")
            self.alarm_setpoint_var.set(str(setpoint) if setpoint is not None else "")
            self.alarm_deadband_var.set(str(deadband) if deadband is not None else "")
            self.alarm_delay_var.set(str(delay_seconds) if delay_seconds is not None else "")
            self.disabled_by_var.set(disabled_by or "")
            self.requires_ack_var.set(bool(requires_ack))
            self.is_enabled_var.set(bool(is_enabled))

            self._set_date_field(self.enabled_date_entry, self.enabled_date_set_var, enabled_date)
            self._set_date_field(self.disabled_date_entry, self.disabled_date_set_var, disabled_date)

            self.alarm_action_text.delete("1.0", tk.END)
            if alarm_action:
                self.alarm_action_text.insert("1.0", alarm_action)

            self.disabled_reason_text.delete("1.0", tk.END)
            if disabled_reason:
                self.disabled_reason_text.insert("1.0", disabled_reason)

        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to load Alarm Configuration record:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error while loading record:\n{e}")

    def _set_date_field(self, entry, set_var, value):
        if value:
            set_var.set(True)
            entry.configure(state="normal")
            entry.set_date(value)
        else:
            set_var.set(False)
            entry.configure(state="disabled")

    def _new_record(self):
        self.selected_id = None
        self.id_var.set("")
        self.instrument_var.set("")
        self.alarm_type_var.set("")
        self.alarm_priority_var.set("")
        self.alarm_description_var.set("")
        self.alarm_setpoint_var.set("")
        self.alarm_deadband_var.set("")
        self.alarm_delay_var.set("")
        self.disabled_by_var.set("")
        self.requires_ack_var.set(True)
        self.is_enabled_var.set(True)

        for entry, set_var in (
            (self.enabled_date_entry, self.enabled_date_set_var),
            (self.disabled_date_entry, self.disabled_date_set_var),
        ):
            set_var.set(False)
            entry.configure(state="disabled")

        self.alarm_action_text.delete("1.0", tk.END)
        self.disabled_reason_text.delete("1.0", tk.END)
        self.tree.selection_remove(self.tree.selection())

    # ------------------------------------------------------------------
    # Save (Insert / Update)
    # ------------------------------------------------------------------
    def _save_record(self):
        instrument_display = self.instrument_var.get().strip()
        if not instrument_display:
            messagebox.showwarning("Validation", "Please select an Instrument.")
            return

        instrument_id = self.instrument_lookup.get(instrument_display)
        if instrument_id is None:
            messagebox.showwarning("Validation", "Please select a valid Instrument from the list.")
            return

        alarm_type = self.alarm_type_var.get().strip() or None
        alarm_priority = self.alarm_priority_var.get().strip() or None
        alarm_description = self.alarm_description_var.get().strip() or None
        disabled_by = self.disabled_by_var.get().strip() or None

        def parse_decimal(var, label):
            raw = var.get().strip()
            if not raw:
                return None, True
            try:
                return float(raw), True
            except ValueError:
                messagebox.showwarning("Validation", f"{label} must be a number.")
                return None, False

        def parse_int(var, label):
            raw = var.get().strip()
            if not raw:
                return None, True
            try:
                return int(raw), True
            except ValueError:
                messagebox.showwarning("Validation", f"{label} must be a whole number.")
                return None, False

        setpoint, ok = parse_decimal(self.alarm_setpoint_var, "Alarm Setpoint")
        if not ok:
            return
        deadband, ok = parse_decimal(self.alarm_deadband_var, "Alarm Deadband")
        if not ok:
            return
        delay_seconds, ok = parse_int(self.alarm_delay_var, "Alarm Delay (seconds)")
        if not ok:
            return

        requires_ack = self.requires_ack_var.get()
        is_enabled = self.is_enabled_var.get()

        enabled_date = self.enabled_date_entry.get_date() if self.enabled_date_set_var.get() else None
        disabled_date = self.disabled_date_entry.get_date() if self.disabled_date_set_var.get() else None

        alarm_action = self.alarm_action_text.get("1.0", tk.END).strip() or None
        disabled_reason = self.disabled_reason_text.get("1.0", tk.END).strip() or None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            if self.selected_id:
                cursor.execute(
                    """
                    UPDATE AlarmConfiguration
                    SET InstrumentID = ?, AlarmType = ?, AlarmDescription = ?, AlarmSetpoint = ?,
                        AlarmDeadband = ?, AlarmDelay_Seconds = ?, AlarmPriority = ?, AlarmAction = ?,
                        RequiresAcknowledgement = ?, IsEnabled = ?, EnabledDate = ?, DisabledDate = ?,
                        DisabledBy = ?, DisabledReason = ?
                    WHERE AlarmID = ?
                    """,
                    (instrument_id, alarm_type, alarm_description, setpoint, deadband,
                     delay_seconds, alarm_priority, alarm_action, requires_ack, is_enabled,
                     enabled_date, disabled_date, disabled_by, disabled_reason, self.selected_id)
                )
                conn.commit()
                messagebox.showinfo("Success", "Alarm Configuration updated successfully.")
            else:
                cursor.execute(
                    """
                    INSERT INTO AlarmConfiguration
                    (InstrumentID, AlarmType, AlarmDescription, AlarmSetpoint, AlarmDeadband,
                     AlarmDelay_Seconds, AlarmPriority, AlarmAction, RequiresAcknowledgement,
                     IsEnabled, EnabledDate, DisabledDate, DisabledBy, DisabledReason)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (instrument_id, alarm_type, alarm_description, setpoint, deadband,
                     delay_seconds, alarm_priority, alarm_action, requires_ack, is_enabled,
                     enabled_date, disabled_date, disabled_by, disabled_reason)
                )
                conn.commit()
                messagebox.showinfo("Success", "Alarm Configuration added successfully.")

            conn.close()
            self.refresh_data()
            self._new_record()

        except pyodbc.IntegrityError as e:
            messagebox.showerror(
                "Integrity Error",
                f"Save failed. This likely indicates an invalid Instrument reference:\n{e}"
            )
        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to save Alarm Configuration:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error while saving:\n{e}")

    # ------------------------------------------------------------------
    # Delete (with dynamic FK dependency check)
    # ------------------------------------------------------------------
    def _get_dependent_records(self, conn, alarm_id):
        """
        Dynamically discover every table with a FK referencing AlarmConfiguration,
        then count rows that reference this AlarmID. This avoids hardcoding
        child table names as the schema keeps growing.
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
                    (alarm_id,)
                )
                count = count_cursor.fetchone()[0]
                if count > 0:
                    dependents.append((child_table, count))
            except pyodbc.Error:
                continue

        return dependents

    def _delete_record(self):
        if not self.selected_id:
            messagebox.showwarning("No Selection", "Please select an Alarm Configuration to delete.")
            return

        try:
            conn = get_connection()
            dependents = self._get_dependent_records(conn, self.selected_id)

            if dependents:
                detail = "\n".join(f"  - {table}: {count} record(s)" for table, count in dependents)
                proceed = messagebox.askyesno(
                    "Alarm Configuration In Use",
                    f"This Alarm Configuration is referenced by other records:\n\n{detail}\n\n"
                    "Deleting it may fail or orphan related data depending on your "
                    "database's FK constraints.\n\nDo you still want to attempt deletion?"
                )
                if not proceed:
                    conn.close()
                    return
            else:
                confirm = messagebox.askyesno(
                    "Confirm Delete",
                    f"Delete this Alarm Configuration (ID {self.selected_id})?"
                )
                if not confirm:
                    conn.close()
                    return

            cursor = conn.cursor()
            cursor.execute("DELETE FROM AlarmConfiguration WHERE AlarmID = ?", (self.selected_id,))
            conn.commit()
            conn.close()

            messagebox.showinfo("Deleted", "Alarm Configuration deleted successfully.")
            self.refresh_data()
            self._new_record()

        except pyodbc.IntegrityError as e:
            messagebox.showerror(
                "Integrity Error",
                f"Cannot delete this Alarm Configuration because other records depend on it:\n{e}"
            )
        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to delete Alarm Configuration:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error while deleting:\n{e}")
