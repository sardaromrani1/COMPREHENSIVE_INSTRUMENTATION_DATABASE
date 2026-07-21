"""
ProcessUnits_form.py
CRUD form for the ProcessUnits table.

Pattern:
- ttk.Treeview list with column-scoped search (keyword for text columns,
  dropdown filters, From/To DateEntry pickers for CommissionDate)
- Detail/edit panel with a required FK combobox for Site
- Save / New / Delete / Refresh buttons
- Identity PK (UnitID) rendered as a disabled entry
- Delete checks for dependent child records dynamically via sys.foreign_keys
  before allowing deletion (ProcessUnits is likely referenced by
  ControlSystems, SubSystems, Instruments, etc. as the schema grows)

Note: the DB's default for TemperatureUnit ('�C') looks like a mojibake
encoding artifact for the degree symbol. This form always writes a clean
UTF-8 '°C' via the combobox rather than reproducing that artifact.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import pyodbc
from datetime import datetime

from db_connection import get_connection


class ProcessUnitsForm(ttk.Frame):

    TABLE_NAME = "ProcessUnits"
    PK_COLUMN = "UnitID"

    UNIT_TYPES = ["Distillation", "Reactor", "Compressor", "Storage", "Utility", "Other"]
    OPERATIONAL_STATUSES = ["Operational", "Shutdown", "Under Maintenance", "Decommissioned", "Standby"]
    PRESSURE_UNITS = ["PSI", "bar", "kPa", "MPa"]
    TEMPERATURE_UNITS = ["\u00b0C", "\u00b0F", "K"] # °C, °F, K
    ATEX_ZONES = ["Zone 0", "Zone 1", "Zone 2", "Zone 20", "Zone 21", "Zone 22", "Non-Hazardous"]
    SIL_LEVELS = ["None", "SIL 1", "SIL 2", "SIL 3", "SIL 4"]

    def __init__(self, parent):
        super().__init__(parent)
        self.selected_id = None
        self.site_lookup = {} # display string -> SiteID

        self._build_ui()
        self._load_site_lookup()
        self.refresh_data()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------
    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        title = ttk.Label(self, text="Process Units", font=("Segoe UI", 14, "bold"))
        title.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 5))

        self._build_search_bar()
        self._build_treeview()
        self._build_detail_panel()

    # -- Search bar -----------------------------------------------------
    def _build_search_bar(self):
        bar = ttk.LabelFrame(self, text="Search")
        bar.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        for c in range(8):
            bar.columnconfigure(c, weight=1)

        ttk.Label(bar, text="Keyword:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.keyword_var = tk.StringVar()
        ttk.Entry(bar, textvariable=self.keyword_var).grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(bar, text="Site:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.site_filter_var = tk.StringVar()
        self.site_filter_combo = ttk.Combobox(
            bar, textvariable=self.site_filter_var, state="readonly", width=20
        )
        self.site_filter_combo.grid(row=0, column=3, sticky="ew", padx=5, pady=5)

        ttk.Label(bar, text="Unit Type:").grid(row=0, column=4, sticky="w", padx=5, pady=5)
        self.type_filter_var = tk.StringVar()
        type_combo = ttk.Combobox(
            bar, textvariable=self.type_filter_var,
            values=["(All)"] + self.UNIT_TYPES, state="readonly", width=15
        )
        type_combo.current(0)
        type_combo.grid(row=0, column=5, sticky="ew", padx=5, pady=5)

        ttk.Label(bar, text="Status:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.status_filter_var = tk.StringVar()
        status_combo = ttk.Combobox(
            bar, textvariable=self.status_filter_var,
            values=["(All)"] + self.OPERATIONAL_STATUSES, state="readonly", width=15
        )
        status_combo.current(0)
        status_combo.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(bar, text="Operational:").grid(row=1, column=2, sticky="w", padx=5, pady=5)
        self.operational_filter_var = tk.StringVar()
        operational_combo = ttk.Combobox(
            bar, textvariable=self.operational_filter_var,
            values=["(All)", "Yes", "No"], state="readonly", width=10
        )
        operational_combo.current(0)
        operational_combo.grid(row=1, column=3, sticky="w", padx=5, pady=5)

        ttk.Label(bar, text="Commission From:").grid(row=1, column=4, sticky="w", padx=5, pady=5)
        self.date_from = DateEntry(bar, date_pattern="yyyy-mm-dd", width=12)
        self.date_from.grid(row=1, column=5, sticky="w", padx=5, pady=5)
        self.date_from_enabled = tk.BooleanVar(value=False)
        ttk.Checkbutton(bar, text="Use", variable=self.date_from_enabled).grid(row=1, column=5, sticky="e")

        ttk.Label(bar, text="To:").grid(row=2, column=4, sticky="e", padx=5, pady=5)
        self.date_to = DateEntry(bar, date_pattern="yyyy-mm-dd", width=12)
        self.date_to.grid(row=2, column=5, sticky="w", padx=5, pady=5)
        self.date_to_enabled = tk.BooleanVar(value=False)
        ttk.Checkbutton(bar, text="Use", variable=self.date_to_enabled).grid(row=2, column=5, sticky="e")

        btn_frame = ttk.Frame(bar)
        btn_frame.grid(row=2, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        ttk.Button(btn_frame, text="Search", command=self.refresh_data).pack(side="left", padx=3)
        ttk.Button(btn_frame, text="Clear", command=self._clear_search).pack(side="left", padx=3)

    def _clear_search(self):
        self.keyword_var.set("")
        self.site_filter_var.set("(All)")
        self.type_filter_var.set("(All)")
        self.status_filter_var.set("(All)")
        self.operational_filter_var.set("(All)")
        self.date_from_enabled.set(False)
        self.date_to_enabled.set(False)
        self.refresh_data()

    # -- Treeview ---------------------------------------------------------
    def _build_treeview(self):
        frame = ttk.Frame(self)
        frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        columns = (
            "UnitID", "UnitCode", "UnitName", "SiteName", "UnitType",
            "DesignCapacity", "CapacityUnit", "OperationalStatus",
            "HazardClass", "SIL_Level", "IsOperational"
        )
        self.tree = ttk.Treeview(frame, columns=columns, show="headings", height=12)

        headings = {
            "UnitID": "ID", "UnitCode": "Unit Code", "UnitName": "Unit Name",
            "SiteName": "Site", "UnitType": "Type", "DesignCapacity": "Design Capacity",
            "CapacityUnit": "Cap. Unit", "OperationalStatus": "Status",
            "HazardClass": "Hazard Class", "SIL_Level": "SIL", "IsOperational": "Operational"
        }
        widths = {
            "UnitID": 50, "UnitCode": 90, "UnitName": 150, "SiteName": 120,
            "UnitType": 100, "DesignCapacity": 100, "CapacityUnit": 70,
            "OperationalStatus": 110, "HazardClass": 90, "SIL_Level": 60,
            "IsOperational": 80
        }
        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor="w")

        vsb = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        self.tree.bind("<<TreeviewSelect>>", self._on_row_select)

    # -- Detail panel -----------------------------------------------------
    def _build_detail_panel(self):
        panel = ttk.LabelFrame(self, text="Process Unit Details")
        panel.grid(row=3, column=0, sticky="ew", padx=10, pady=(5, 10))
        for c in range(4):
            panel.columnconfigure(c, weight=1)

        # UnitID (disabled, identity)
        ttk.Label(panel, text="Unit ID:").grid(row=0, column=0, sticky="w", padx=5, pady=4)
        self.id_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.id_var, state="disabled", width=10).grid(
            row=0, column=1, sticky="w", padx=5, pady=4
        )

        # Site (FK combo, required)
        ttk.Label(panel, text="Site *:").grid(row=0, column=2, sticky="w", padx=5, pady=4)
        self.site_var = tk.StringVar()
        self.site_combo = ttk.Combobox(panel, textvariable=self.site_var, state="readonly", width=25)
        self.site_combo.grid(row=0, column=3, sticky="ew", padx=5, pady=4)

        # UnitCode (required, unique)
        ttk.Label(panel, text="Unit Code *:").grid(row=1, column=0, sticky="w", padx=5, pady=4)
        self.code_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.code_var, width=20).grid(
            row=1, column=1, sticky="ew", padx=5, pady=4
        )

        # UnitName (required)
        ttk.Label(panel, text="Unit Name *:").grid(row=1, column=2, sticky="w", padx=5, pady=4)
        self.name_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.name_var, width=25).grid(
            row=1, column=3, sticky="ew", padx=5, pady=4
        )

        # UnitType
        ttk.Label(panel, text="Unit Type:").grid(row=2, column=0, sticky="w", padx=5, pady=4)
        self.type_var = tk.StringVar()
        ttk.Combobox(panel, textvariable=self.type_var, values=self.UNIT_TYPES, width=18).grid(
            row=2, column=1, sticky="ew", padx=5, pady=4
        )

        # OperationalStatus
        ttk.Label(panel, text="Operational Status:").grid(row=2, column=2, sticky="w", padx=5, pady=4)
        self.status_var = tk.StringVar(value="Operational")
        ttk.Combobox(
            panel, textvariable=self.status_var, values=self.OPERATIONAL_STATUSES,
            state="readonly", width=18
        ).grid(row=2, column=3, sticky="ew", padx=5, pady=4)

        # DesignCapacity / CapacityUnit
        ttk.Label(panel, text="Design Capacity:").grid(row=3, column=0, sticky="w", padx=5, pady=4)
        self.capacity_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.capacity_var, width=15).grid(
            row=3, column=1, sticky="w", padx=5, pady=4
        )

        ttk.Label(panel, text="Capacity Unit:").grid(row=3, column=2, sticky="w", padx=5, pady=4)
        self.capacity_unit_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.capacity_unit_var, width=15).grid(
            row=3, column=3, sticky="w", padx=5, pady=4
        )

        # OperatingPressure / PressureUnit
        ttk.Label(panel, text="Operating Pressure:").grid(row=4, column=0, sticky="w", padx=5, pady=4)
        self.pressure_var = tk.StringVar()
        pressure_frame = ttk.Frame(panel)
        pressure_frame.grid(row=4, column=1, sticky="w", padx=5, pady=4)
        ttk.Entry(pressure_frame, textvariable=self.pressure_var, width=10).pack(side="left")
        self.pressure_unit_var = tk.StringVar(value="PSI")
        ttk.Combobox(
            pressure_frame, textvariable=self.pressure_unit_var, values=self.PRESSURE_UNITS,
            state="readonly", width=6
        ).pack(side="left", padx=3)

        # OperatingTemperature / TemperatureUnit
        ttk.Label(panel, text="Operating Temperature:").grid(row=4, column=2, sticky="w", padx=5, pady=4)
        self.temperature_var = tk.StringVar()
        temp_frame = ttk.Frame(panel)
        temp_frame.grid(row=4, column=3, sticky="w", padx=5, pady=4)
        ttk.Entry(temp_frame, textvariable=self.temperature_var, width=10).pack(side="left")
        self.temperature_unit_var = tk.StringVar(value="\u00b0C")
        ttk.Combobox(
            temp_frame, textvariable=self.temperature_unit_var, values=self.TEMPERATURE_UNITS,
            state="readonly", width=6
        ).pack(side="left", padx=3)

        # CommissionDate (nullable -> "Set" checkbox + DateEntry)
        ttk.Label(panel, text="Commission Date:").grid(row=5, column=0, sticky="w", padx=5, pady=4)
        date_frame = ttk.Frame(panel)
        date_frame.grid(row=5, column=1, sticky="w", padx=5, pady=4)
        self.commission_set_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            date_frame, text="Set", variable=self.commission_set_var,
            command=self._toggle_commission_date
        ).pack(side="left")
        self.commission_date = DateEntry(date_frame, date_pattern="yyyy-mm-dd", width=12, state="disabled")
        self.commission_date.pack(side="left", padx=5)

        # HazardClass
        ttk.Label(panel, text="Hazard Class:").grid(row=5, column=2, sticky="w", padx=5, pady=4)
        self.hazard_class_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.hazard_class_var, width=18).grid(
            row=5, column=3, sticky="ew", padx=5, pady=4
        )

        # ATEX_Zone
        ttk.Label(panel, text="ATEX Zone:").grid(row=6, column=0, sticky="w", padx=5, pady=4)
        self.atex_zone_var = tk.StringVar()
        ttk.Combobox(panel, textvariable=self.atex_zone_var, values=self.ATEX_ZONES, width=18).grid(
            row=6, column=1, sticky="ew", padx=5, pady=4
        )

        # SIL_Level
        ttk.Label(panel, text="SIL Level:").grid(row=6, column=2, sticky="w", padx=5, pady=4)
        self.sil_level_var = tk.StringVar()
        ttk.Combobox(
            panel, textvariable=self.sil_level_var, values=self.SIL_LEVELS,
            state="readonly", width=18
        ).grid(row=6, column=3, sticky="ew", padx=5, pady=4)

        # IsOperational
        self.operational_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(panel, text="Operational", variable=self.operational_var).grid(
            row=7, column=0, sticky="w", padx=5, pady=4
        )

        ttk.Label(panel, text="* Required fields", foreground="gray").grid(
            row=7, column=1, columnspan=2, sticky="w", padx=5, pady=4
        )

        # Action buttons
        action_frame = ttk.Frame(panel)
        action_frame.grid(row=8, column=0, columnspan=4, sticky="e", padx=5, pady=(10, 5))
        ttk.Button(action_frame, text="New", command=self._new_record).pack(side="left", padx=3)
        ttk.Button(action_frame, text="Save", command=self._save_record).pack(side="left", padx=3)
        ttk.Button(action_frame, text="Delete", command=self._delete_record).pack(side="left", padx=3)
        ttk.Button(action_frame, text="Refresh", command=self.refresh_data).pack(side="left", padx=3)
        ttk.Button(action_frame, text="Reload Sites", command=self._load_site_lookup).pack(side="left", padx=3)

    def _toggle_commission_date(self):
        self.commission_date.configure(state="normal" if self.commission_set_var.get() else "disabled")

    # ------------------------------------------------------------------
    # Site FK lookup
    # ------------------------------------------------------------------
    def _load_site_lookup(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT SiteID, SiteName, SiteCode FROM Sites ORDER BY SiteName")
            rows = cursor.fetchall()
            conn.close()

            self.site_lookup = {}
            display_values = []
            for site_id, site_name, site_code in rows:
                display = f"{site_name} ({site_code})"
                self.site_lookup[display] = site_id
                display_values.append(display)

            self.site_combo["values"] = display_values
            self.site_filter_combo["values"] = ["(All)"] + display_values
            if not self.site_filter_var.get():
                self.site_filter_var.set("(All)")

        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to load Sites lookup:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error while loading Sites:\n{e}")

    # ------------------------------------------------------------------
    # Data loading / search
    # ------------------------------------------------------------------
    def refresh_data(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()

            query = """
                SELECT pu.UnitID, pu.UnitCode, pu.UnitName, s.SiteName, pu.UnitType,
                       pu.DesignCapacity, pu.CapacityUnit, pu.OperationalStatus,
                       pu.HazardClass, pu.SIL_Level, pu.IsOperational
                FROM ProcessUnits pu
                LEFT JOIN Sites s ON pu.SiteID = s.SiteID
                WHERE 1 = 1
            """
            params = []

            keyword = self.keyword_var.get().strip()
            if keyword:
                query += """ AND (
                    pu.UnitCode LIKE ? OR pu.UnitName LIKE ? OR pu.HazardClass LIKE ?
                )"""
                like = f"%{keyword}%"
                params.extend([like, like, like])

            site_display = self.site_filter_var.get()
            if site_display and site_display != "(All)":
                site_id = self.site_lookup.get(site_display)
                if site_id is not None:
                    query += " AND pu.SiteID = ?"
                    params.append(site_id)

            unit_type = self.type_filter_var.get()
            if unit_type and unit_type != "(All)":
                query += " AND pu.UnitType = ?"
                params.append(unit_type)

            status = self.status_filter_var.get()
            if status and status != "(All)":
                query += " AND pu.OperationalStatus = ?"
                params.append(status)

            operational = self.operational_filter_var.get()
            if operational == "Yes":
                query += " AND pu.IsOperational = 1"
            elif operational == "No":
                query += " AND pu.IsOperational = 0"

            if self.date_from_enabled.get():
                query += " AND pu.CommissionDate >= ?"
                params.append(self.date_from.get_date())

            if self.date_to_enabled.get():
                query += " AND pu.CommissionDate <= ?"
                params.append(self.date_to.get_date())

            query += " ORDER BY pu.UnitName"

            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()

            self.tree.delete(*self.tree.get_children())
            for row in rows:
                values = list(row)
                values[10] = "Yes" if values[10] else "No" # IsOperational
                self.tree.insert("", "end", values=values)

        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to load Process Units data:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error while loading data:\n{e}")

    # ------------------------------------------------------------------
    # Selection handling
    # ------------------------------------------------------------------
    def _on_row_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return

        values = self.tree.item(selected[0], "values")
        self.selected_id = values[0]

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT SiteID, UnitCode, UnitName, UnitType, DesignCapacity, CapacityUnit,
                       OperatingPressure, OperatingTemperature, PressureUnit, TemperatureUnit,
                       CommissionDate, OperationalStatus, HazardClass, ATEX_Zone, SIL_Level,
                       IsOperational
                FROM ProcessUnits WHERE UnitID = ?
                """,
                (self.selected_id,)
            )
            row = cursor.fetchone()
            conn.close()

            if row is None:
                return

            (site_id, unit_code, unit_name, unit_type, design_capacity, capacity_unit,
             operating_pressure, operating_temperature, pressure_unit, temperature_unit,
             commission_date, operational_status, hazard_class, atex_zone, sil_level,
             is_operational) = row

            self.id_var.set(self.selected_id)

            site_display = next(
                (disp for disp, sid in self.site_lookup.items() if sid == site_id), ""
            )
            self.site_var.set(site_display)

            self.code_var.set(unit_code)
            self.name_var.set(unit_name)
            self.type_var.set(unit_type or "")
            self.capacity_var.set(str(design_capacity) if design_capacity is not None else "")
            self.capacity_unit_var.set(capacity_unit or "")
            self.pressure_var.set(str(operating_pressure) if operating_pressure is not None else "")
            self.temperature_var.set(str(operating_temperature) if operating_temperature is not None else "")
            self.pressure_unit_var.set(pressure_unit or "PSI")
            self.temperature_unit_var.set(temperature_unit or "\u00b0C")

            if commission_date:
                self.commission_set_var.set(True)
                self.commission_date.configure(state="normal")
                self.commission_date.set_date(commission_date)
            else:
                self.commission_set_var.set(False)
                self.commission_date.configure(state="disabled")

            self.status_var.set(operational_status or "Operational")
            self.hazard_class_var.set(hazard_class or "")
            self.atex_zone_var.set(atex_zone or "")
            self.sil_level_var.set(sil_level or "")
            self.operational_var.set(bool(is_operational))

        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to load Process Unit details:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error while loading details:\n{e}")

    def _new_record(self):
        self.selected_id = None
        self.tree.selection_remove(self.tree.selection())

        self.id_var.set("")
        self.site_var.set("")
        self.code_var.set("")
        self.name_var.set("")
        self.type_var.set("")
        self.capacity_var.set("")
        self.capacity_unit_var.set("")
        self.pressure_var.set("")
        self.temperature_var.set("")
        self.pressure_unit_var.set("PSI")
        self.temperature_unit_var.set("\u00b0C")
        self.commission_set_var.set(False)
        self.commission_date.configure(state="disabled")
        self.status_var.set("Operational")
        self.hazard_class_var.set("")
        self.atex_zone_var.set("")
        self.sil_level_var.set("")
        self.operational_var.set(True)

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    def _validate_decimal(self, value_str, field_label):
        """Returns (is_valid, float_value_or_None)."""
        value_str = value_str.strip()
        if not value_str:
            return True, None
        try:
            return True, float(value_str)
        except ValueError:
            messagebox.showwarning("Validation", f"{field_label} must be a valid number.")
            return False, None

    def _validate_form(self):
        if not self.site_var.get().strip():
            messagebox.showwarning("Validation", "Site is required.")
            return False
        if not self.code_var.get().strip():
            messagebox.showwarning("Validation", "Unit Code is required.")
            return False
        if not self.name_var.get().strip():
            messagebox.showwarning("Validation", "Unit Name is required.")
            return False
        return True

    # ------------------------------------------------------------------
    # Save (Insert / Update)
    # ------------------------------------------------------------------
    def _save_record(self):
        if not self._validate_form():
            return

        ok, design_capacity = self._validate_decimal(self.capacity_var.get(), "Design Capacity")
        if not ok:
            return
        ok, operating_pressure = self._validate_decimal(self.pressure_var.get(), "Operating Pressure")
        if not ok:
            return
        ok, operating_temperature = self._validate_decimal(self.temperature_var.get(), "Operating Temperature")
        if not ok:
            return

        site_id = self.site_lookup.get(self.site_var.get())
        if site_id is None:
            messagebox.showwarning("Validation", "Please select a valid Site.")
            return

        unit_code = self.code_var.get().strip()
        unit_name = self.name_var.get().strip()
        unit_type = self.type_var.get().strip() or None
        capacity_unit = self.capacity_unit_var.get().strip() or None
        pressure_unit = self.pressure_unit_var.get().strip() or None
        temperature_unit = self.temperature_unit_var.get().strip() or None
        commission_date = self.commission_date.get_date() if self.commission_set_var.get() else None
        operational_status = self.status_var.get().strip() or "Operational"
        hazard_class = self.hazard_class_var.get().strip() or None
        atex_zone = self.atex_zone_var.get().strip() or None
        sil_level = self.sil_level_var.get().strip() or None
        is_operational = 1 if self.operational_var.get() else 0

        try:
            conn = get_connection()
            cursor = conn.cursor()

            if self.selected_id:
                cursor.execute(
                    """
                    UPDATE ProcessUnits
                    SET SiteID = ?, UnitCode = ?, UnitName = ?, UnitType = ?,
                        DesignCapacity = ?, CapacityUnit = ?, OperatingPressure = ?,
                        OperatingTemperature = ?, PressureUnit = ?, TemperatureUnit = ?,
                        CommissionDate = ?, OperationalStatus = ?, HazardClass = ?,
                        ATEX_Zone = ?, SIL_Level = ?, IsOperational = ?
                    WHERE UnitID = ?
                    """,
                    (site_id, unit_code, unit_name, unit_type, design_capacity, capacity_unit,
                     operating_pressure, operating_temperature, pressure_unit, temperature_unit,
                     commission_date, operational_status, hazard_class, atex_zone, sil_level,
                     is_operational, self.selected_id)
                )
                conn.commit()
                messagebox.showinfo("Success", "Process Unit updated successfully.")
            else:
                cursor.execute(
                    """
                    INSERT INTO ProcessUnits
                        (SiteID, UnitCode, UnitName, UnitType, DesignCapacity, CapacityUnit,
                         OperatingPressure, OperatingTemperature, PressureUnit, TemperatureUnit,
                         CommissionDate, OperationalStatus, HazardClass, ATEX_Zone, SIL_Level,
                         IsOperational)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (site_id, unit_code, unit_name, unit_type, design_capacity, capacity_unit,
                     operating_pressure, operating_temperature, pressure_unit, temperature_unit,
                     commission_date, operational_status, hazard_class, atex_zone, sil_level,
                     is_operational)
                )
                conn.commit()
                messagebox.showinfo("Success", "Process Unit added successfully.")

            conn.close()
            self.refresh_data()
            self._new_record()

        except pyodbc.IntegrityError as e:
            messagebox.showerror(
                "Integrity Error",
                f"Save failed. This likely violates a unique constraint "
                f"(Unit Code must be unique) or an invalid Site reference:\n{e}"
            )
        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to save Process Unit:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error while saving:\n{e}")

    # ------------------------------------------------------------------
    # Delete (with dynamic FK dependency check)
    # ------------------------------------------------------------------
    def _get_dependent_records(self, conn, unit_id):
        """
        Dynamically discover every table with a FK referencing ProcessUnits,
        then count rows that reference this UnitID. This avoids hardcoding
        child table names, which matters since the schema keeps growing.
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
                    (unit_id,)
                )
                count = count_cursor.fetchone()[0]
                if count > 0:
                    dependents.append((child_table, count))
            except pyodbc.Error:
                continue

        return dependents

    def _delete_record(self):
        if not self.selected_id:
            messagebox.showwarning("No Selection", "Please select a Process Unit to delete.")
            return

        try:
            conn = get_connection()
            dependents = self._get_dependent_records(conn, self.selected_id)

            if dependents:
                detail = "\n".join(f" - {table}: {count} record(s)" for table, count in dependents)
                proceed = messagebox.askyesno(
                    "Process Unit In Use",
                    f"This Process Unit is referenced by other records:\n\n{detail}\n\n"
                    "Deleting it may fail or orphan related data depending on your "
                    "database's FK constraints.\n\nDo you still want to attempt deletion?"
                )
                if not proceed:
                    conn.close()
                    return
            else:
                confirm = messagebox.askyesno(
                    "Confirm Delete",
                    f"Delete Process Unit '{self.name_var.get()}' (ID {self.selected_id})?"
                )
                if not confirm:
                    conn.close()
                    return

            cursor = conn.cursor()
            cursor.execute("DELETE FROM ProcessUnits WHERE UnitID = ?", (self.selected_id,))
            conn.commit()
            conn.close()

            messagebox.showinfo("Deleted", "Process Unit deleted successfully.")
            self.refresh_data()
            self._new_record()

        except pyodbc.IntegrityError as e:
            messagebox.showerror(
                "Integrity Error",
                f"Cannot delete this Process Unit because other records depend on it:\n{e}"
            )
        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to delete Process Unit:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error while deleting:\n{e}")
