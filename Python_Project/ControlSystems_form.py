"""
ControlSystems_form.py

CRUD form for the ControlSystems table.

    CREATE TABLE ControlSystems (
        SystemID INT PRIMARY KEY IDENTITY(1,1),
        UnitID INT,
        SystemCode NVARCHAR(20) UNIQUE NOT NULL,
        SystemName NVARCHAR(100) NOT NULL,
        SystemType NVARCHAR(50),
        Manufacturer NVARCHAR(100),
        Model NVARCHAR(100),
        SoftwareVersion NVARCHAR(50),
        FirmwareVersion NVARCHAR(50),
        InstallDate DATE,
        CommissionDate DATE,
        LastUpgradeDate DATE,
        RedundancyLevel NVARCHAR(20),
        CommunicationProtocol NVARCHAR(100),
        IsActive BIT DEFAULT 1,
        MaintenanceContract NVARCHAR(100),
        ContractExpiryDate DATE,
        FOREIGN KEY (UnitID) REFERENCES ProcessUnits(UnitID)
    );

Follows the same conventions as the other forms in this project:
    - get_connection() from db_connection (pyodbc / ODBC Driver 17 / Windows Auth)
    - FK combobox (UnitID -> ProcessUnits) showing a human-readable label,
      storing the integer ID
    - Nullable dates handled with a "Set" checkbox + tkcalendar DateEntry
    - BIT column (IsActive) rendered as a checkbutton
    - pyodbc.IntegrityError caught separately for meaningful constraint messages
    - Dynamic FK-dependency check on delete using sys.foreign_keys
    - Column-scoped search / filter panel with live keyword filtering
"""

import tkinter as tk
from tkinter import ttk, messagebox

import pyodbc
from tkcalendar import DateEntry

from db_connection import get_connection


SYSTEM_TYPES = ["DCS", "PLC", "SCADA", "ESD", "F&G", "BMS", "SIS"]
REDUNDANCY_LEVELS = ["None", "Dual", "Triple"]


class ControlSystemsForm(ttk.Frame):
    TABLE_NAME = "ControlSystems"

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.selected_id = None
        self.unit_lookup = {}   # display string -> UnitID

        self._build_ui()
        self._load_unit_lookup()
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
            values=["(All Columns)", "SystemCode", "SystemName", "Manufacturer", "Model"]
        )
        self.search_column_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=4)

        ttk.Label(filter_frame, text="Keyword:").grid(row=0, column=2, sticky="w", padx=5, pady=4)
        self.search_text_var = tk.StringVar()
        search_entry = ttk.Entry(filter_frame, textvariable=self.search_text_var, width=28)
        search_entry.grid(row=0, column=3, sticky="ew", padx=5, pady=4)
        search_entry.bind("<KeyRelease>", lambda e: self.refresh_data())

        ttk.Label(filter_frame, text="Process Unit:").grid(row=1, column=0, sticky="w", padx=5, pady=4)
        self.unit_filter_var = tk.StringVar()
        self.unit_filter_combo = ttk.Combobox(
            filter_frame, textvariable=self.unit_filter_var, state="readonly", width=28
        )
        self.unit_filter_combo.grid(row=1, column=1, sticky="ew", padx=5, pady=4)
        self.unit_filter_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_data())

        ttk.Label(filter_frame, text="System Type:").grid(row=1, column=2, sticky="w", padx=5, pady=4)
        self.type_filter_var = tk.StringVar(value="(All)")
        self.type_filter_combo = ttk.Combobox(
            filter_frame, textvariable=self.type_filter_var, state="readonly", width=18,
            values=["(All)"] + SYSTEM_TYPES
        )
        self.type_filter_combo.grid(row=1, column=3, sticky="ew", padx=5, pady=4)
        self.type_filter_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_data())

        btn_frame = ttk.Frame(filter_frame)
        btn_frame.grid(row=2, column=0, columnspan=4, sticky="w", padx=5, pady=(0, 4))
        ttk.Button(btn_frame, text="Apply Filter", command=self.refresh_data).pack(side="left", padx=3)
        ttk.Button(btn_frame, text="Clear Filter", command=self._clear_filter).pack(side="left", padx=3)

        for col in range(4):
            filter_frame.columnconfigure(col, weight=1)

        # ---------------- Treeview ----------------
        tree_frame = ttk.Frame(self)
        tree_frame.pack(side="top", fill="both", expand=True, padx=8, pady=4)

        columns = ("SystemID", "SystemCode", "SystemName", "SystemType",
                   "ProcessUnit", "RedundancyLevel", "IsActive")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=10)
        headings = {
            "SystemID": "ID", "SystemCode": "System Code", "SystemName": "System Name",
            "SystemType": "Type", "ProcessUnit": "Process Unit",
            "RedundancyLevel": "Redundancy", "IsActive": "Active",
        }
        widths = {
            "SystemID": 50, "SystemCode": 100, "SystemName": 160, "SystemType": 80,
            "ProcessUnit": 200, "RedundancyLevel": 90, "IsActive": 60,
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
        panel = ttk.LabelFrame(self, text="Control System Details")
        panel.pack(side="top", fill="x", padx=8, pady=4)
        for col in range(4):
            panel.columnconfigure(col, weight=1)

        # SystemID (disabled, identity)
        ttk.Label(panel, text="System ID:").grid(row=0, column=0, sticky="w", padx=5, pady=4)
        self.id_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.id_var, width=20, state="disabled").grid(
            row=0, column=1, sticky="ew", padx=5, pady=4
        )

        # Process Unit (FK combobox, nullable)
        ttk.Label(panel, text="Process Unit:").grid(row=0, column=2, sticky="w", padx=5, pady=4)
        self.unit_var = tk.StringVar()
        self.unit_combo = ttk.Combobox(panel, textvariable=self.unit_var, state="readonly", width=28)
        self.unit_combo.grid(row=0, column=3, sticky="ew", padx=5, pady=4)

        # SystemCode (required, unique)
        ttk.Label(panel, text="System Code *:").grid(row=1, column=0, sticky="w", padx=5, pady=4)
        self.system_code_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.system_code_var, width=20).grid(
            row=1, column=1, sticky="ew", padx=5, pady=4
        )

        # SystemName (required)
        ttk.Label(panel, text="System Name *:").grid(row=1, column=2, sticky="w", padx=5, pady=4)
        self.system_name_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.system_name_var, width=28).grid(
            row=1, column=3, sticky="ew", padx=5, pady=4
        )

        # SystemType
        ttk.Label(panel, text="System Type:").grid(row=2, column=0, sticky="w", padx=5, pady=4)
        self.system_type_var = tk.StringVar()
        self.system_type_combo = ttk.Combobox(
            panel, textvariable=self.system_type_var, width=18, values=SYSTEM_TYPES
        )
        self.system_type_combo.grid(row=2, column=1, sticky="ew", padx=5, pady=4)

        # RedundancyLevel
        ttk.Label(panel, text="Redundancy Level:").grid(row=2, column=2, sticky="w", padx=5, pady=4)
        self.redundancy_var = tk.StringVar()
        self.redundancy_combo = ttk.Combobox(
            panel, textvariable=self.redundancy_var, width=26, values=REDUNDANCY_LEVELS
        )
        self.redundancy_combo.grid(row=2, column=3, sticky="ew", padx=5, pady=4)

        # Manufacturer
        ttk.Label(panel, text="Manufacturer:").grid(row=3, column=0, sticky="w", padx=5, pady=4)
        self.manufacturer_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.manufacturer_var, width=20).grid(
            row=3, column=1, sticky="ew", padx=5, pady=4
        )

        # Model
        ttk.Label(panel, text="Model:").grid(row=3, column=2, sticky="w", padx=5, pady=4)
        self.model_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.model_var, width=28).grid(
            row=3, column=3, sticky="ew", padx=5, pady=4
        )

        # SoftwareVersion
        ttk.Label(panel, text="Software Version:").grid(row=4, column=0, sticky="w", padx=5, pady=4)
        self.software_version_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.software_version_var, width=20).grid(
            row=4, column=1, sticky="ew", padx=5, pady=4
        )

        # FirmwareVersion
        ttk.Label(panel, text="Firmware Version:").grid(row=4, column=2, sticky="w", padx=5, pady=4)
        self.firmware_version_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.firmware_version_var, width=28).grid(
            row=4, column=3, sticky="ew", padx=5, pady=4
        )

        # CommunicationProtocol
        ttk.Label(panel, text="Communication Protocol:").grid(row=5, column=0, sticky="w", padx=5, pady=4)
        self.comm_protocol_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.comm_protocol_var, width=20).grid(
            row=5, column=1, sticky="ew", padx=5, pady=4
        )

        # MaintenanceContract
        ttk.Label(panel, text="Maintenance Contract:").grid(row=5, column=2, sticky="w", padx=5, pady=4)
        self.maintenance_contract_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.maintenance_contract_var, width=28).grid(
            row=5, column=3, sticky="ew", padx=5, pady=4
        )

        # IsActive (bit)
        ttk.Label(panel, text="Is Active:").grid(row=6, column=0, sticky="w", padx=5, pady=4)
        self.is_active_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(panel, variable=self.is_active_var).grid(
            row=6, column=1, sticky="w", padx=5, pady=4
        )

        # ---- Nullable dates: InstallDate, CommissionDate, LastUpgradeDate, ContractExpiryDate ----
        date_frame = ttk.LabelFrame(panel, text="Dates")
        date_frame.grid(row=7, column=0, columnspan=4, sticky="ew", padx=5, pady=(8, 4))
        for col in range(4):
            date_frame.columnconfigure(col, weight=1)

        self.install_date_set_var = tk.BooleanVar(value=False)
        self.install_date_entry = self._make_date_field(
            date_frame, "Install Date:", self.install_date_set_var, row=0, col=0
        )

        self.commission_date_set_var = tk.BooleanVar(value=False)
        self.commission_date_entry = self._make_date_field(
            date_frame, "Commission Date:", self.commission_date_set_var, row=0, col=2
        )

        self.last_upgrade_date_set_var = tk.BooleanVar(value=False)
        self.last_upgrade_date_entry = self._make_date_field(
            date_frame, "Last Upgrade Date:", self.last_upgrade_date_set_var, row=1, col=0
        )

        self.contract_expiry_date_set_var = tk.BooleanVar(value=False)
        self.contract_expiry_date_entry = self._make_date_field(
            date_frame, "Contract Expiry Date:", self.contract_expiry_date_set_var, row=1, col=2
        )

        ttk.Label(panel, text="* Required fields", foreground="gray").grid(
            row=8, column=0, columnspan=2, sticky="w", padx=5, pady=4
        )

        # Action buttons
        action_frame = ttk.Frame(panel)
        action_frame.grid(row=9, column=0, columnspan=4, sticky="e", padx=5, pady=(10, 5))
        ttk.Button(action_frame, text="New", command=self._new_record).pack(side="left", padx=3)
        ttk.Button(action_frame, text="Save", command=self._save_record).pack(side="left", padx=3)
        ttk.Button(action_frame, text="Delete", command=self._delete_record).pack(side="left", padx=3)
        ttk.Button(action_frame, text="Refresh", command=self.refresh_data).pack(side="left", padx=3)
        ttk.Button(action_frame, text="Reload Units", command=self._load_unit_lookup).pack(
            side="left", padx=3
        )

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
        self.unit_filter_var.set("(All)" if "(All)" in self.unit_filter_combo["values"] else "")
        self.type_filter_combo.set("(All)")
        self.search_text_var.set("")
        self.refresh_data()

    # ------------------------------------------------------------------
    # Process Unit FK lookup
    # ------------------------------------------------------------------
    def _load_unit_lookup(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT pu.UnitID, pu.UnitName, pu.UnitCode, s.SiteName
                FROM ProcessUnits pu
                LEFT JOIN Sites s ON pu.SiteID = s.SiteID
                ORDER BY s.SiteName, pu.UnitName
                """
            )
            rows = cursor.fetchall()
            conn.close()

            self.unit_lookup = {}
            display_values = []
            for unit_id, unit_name, unit_code, site_name in rows:
                display = f"{unit_name} ({unit_code}) - {site_name or 'No Site'}"
                self.unit_lookup[display] = unit_id
                display_values.append(display)

            self.unit_combo["values"] = display_values
            self.unit_filter_combo["values"] = ["(All)"] + display_values
            if not self.unit_filter_var.get():
                self.unit_filter_var.set("(All)")

        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to load Process Units lookup:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error while loading Process Units:\n{e}")

    def _unit_display_for_id(self, unit_id):
        if unit_id is None:
            return ""
        for display, uid in self.unit_lookup.items():
            if uid == unit_id:
                return display
        return f"[ID {unit_id}]"

    # ------------------------------------------------------------------
    # Data loading / search
    # ------------------------------------------------------------------
    def refresh_data(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()

            query = """
                SELECT cs.SystemID, cs.SystemCode, cs.SystemName, cs.SystemType,
                       pu.UnitName, pu.UnitCode, cs.RedundancyLevel, cs.IsActive
                FROM ControlSystems cs
                LEFT JOIN ProcessUnits pu ON cs.UnitID = pu.UnitID
                WHERE 1=1
            """
            params = []

            keyword = self.search_text_var.get().strip()
            if keyword:
                column = self.search_column_var.get()
                like_value = f"%{keyword}%"
                searchable_columns = ["SystemCode", "SystemName", "Manufacturer", "Model"]
                if column in searchable_columns:
                    query += f" AND cs.{column} LIKE ?"
                    params.append(like_value)
                else:
                    conditions = " OR ".join(f"cs.{c} LIKE ?" for c in searchable_columns)
                    query += f" AND ({conditions})"
                    params.extend([like_value] * len(searchable_columns))

            unit_display = self.unit_filter_var.get()
            if unit_display and unit_display != "(All)":
                unit_id = self.unit_lookup.get(unit_display)
                if unit_id is not None:
                    query += " AND cs.UnitID = ?"
                    params.append(unit_id)

            type_filter = self.type_filter_var.get()
            if type_filter and type_filter != "(All)":
                query += " AND cs.SystemType = ?"
                params.append(type_filter)

            query += " ORDER BY cs.SystemCode"

            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()

            for item in self.tree.get_children():
                self.tree.delete(item)

            for row in rows:
                (system_id, system_code, system_name, system_type,
                 unit_name, unit_code, redundancy_level, is_active) = row
                unit_label = f"{unit_name} ({unit_code})" if unit_name else ""
                self.tree.insert(
                    "", "end", iid=str(system_id),
                    values=(
                        system_id, system_code, system_name, system_type or "",
                        unit_label, redundancy_level or "",
                        "Yes" if is_active else "No",
                    )
                )

        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to load Control Systems data:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error while loading data:\n{e}")

    # ------------------------------------------------------------------
    # Selection / form population
    # ------------------------------------------------------------------
    def _on_select(self, event):
        selection = self.tree.selection()
        if not selection:
            return

        system_id = int(selection[0])
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT SystemID, UnitID, SystemCode, SystemName, SystemType,
                       Manufacturer, Model, SoftwareVersion, FirmwareVersion,
                       InstallDate, CommissionDate, LastUpgradeDate, RedundancyLevel,
                       CommunicationProtocol, IsActive, MaintenanceContract, ContractExpiryDate
                FROM ControlSystems
                WHERE SystemID = ?
                """,
                (system_id,)
            )
            row = cursor.fetchone()
            conn.close()

            if not row:
                return

            (sid, unit_id, system_code, system_name, system_type, manufacturer, model,
             software_version, firmware_version, install_date, commission_date,
             last_upgrade_date, redundancy_level, comm_protocol, is_active,
             maintenance_contract, contract_expiry_date) = row

            self.selected_id = sid
            self.id_var.set(str(sid))
            self.unit_var.set(self._unit_display_for_id(unit_id))
            self.system_code_var.set(system_code or "")
            self.system_name_var.set(system_name or "")
            self.system_type_var.set(system_type or "")
            self.manufacturer_var.set(manufacturer or "")
            self.model_var.set(model or "")
            self.software_version_var.set(software_version or "")
            self.firmware_version_var.set(firmware_version or "")
            self.redundancy_var.set(redundancy_level or "")
            self.comm_protocol_var.set(comm_protocol or "")
            self.maintenance_contract_var.set(maintenance_contract or "")
            self.is_active_var.set(bool(is_active))

            self._set_date_field(self.install_date_entry, self.install_date_set_var, install_date)
            self._set_date_field(self.commission_date_entry, self.commission_date_set_var, commission_date)
            self._set_date_field(
                self.last_upgrade_date_entry, self.last_upgrade_date_set_var, last_upgrade_date
            )
            self._set_date_field(
                self.contract_expiry_date_entry, self.contract_expiry_date_set_var, contract_expiry_date
            )

        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to load Control System record:\n{e}")
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
        self.unit_var.set("")
        self.system_code_var.set("")
        self.system_name_var.set("")
        self.system_type_var.set("")
        self.manufacturer_var.set("")
        self.model_var.set("")
        self.software_version_var.set("")
        self.firmware_version_var.set("")
        self.redundancy_var.set("")
        self.comm_protocol_var.set("")
        self.maintenance_contract_var.set("")
        self.is_active_var.set(True)

        for entry, set_var in (
            (self.install_date_entry, self.install_date_set_var),
            (self.commission_date_entry, self.commission_date_set_var),
            (self.last_upgrade_date_entry, self.last_upgrade_date_set_var),
            (self.contract_expiry_date_entry, self.contract_expiry_date_set_var),
        ):
            set_var.set(False)
            entry.configure(state="disabled")

        self.tree.selection_remove(self.tree.selection())

    # ------------------------------------------------------------------
    # Save (Insert / Update)
    # ------------------------------------------------------------------
    def _save_record(self):
        system_code = self.system_code_var.get().strip()
        system_name = self.system_name_var.get().strip()

        if not system_code:
            messagebox.showwarning("Validation", "Please enter a System Code.")
            return
        if not system_name:
            messagebox.showwarning("Validation", "Please enter a System Name.")
            return

        unit_display = self.unit_var.get().strip()
        unit_id = self.unit_lookup.get(unit_display) if unit_display else None

        system_type = self.system_type_var.get().strip() or None
        manufacturer = self.manufacturer_var.get().strip() or None
        model = self.model_var.get().strip() or None
        software_version = self.software_version_var.get().strip() or None
        firmware_version = self.firmware_version_var.get().strip() or None
        redundancy_level = self.redundancy_var.get().strip() or None
        comm_protocol = self.comm_protocol_var.get().strip() or None
        maintenance_contract = self.maintenance_contract_var.get().strip() or None
        is_active = self.is_active_var.get()

        install_date = self.install_date_entry.get_date() if self.install_date_set_var.get() else None
        commission_date = (
            self.commission_date_entry.get_date() if self.commission_date_set_var.get() else None
        )
        last_upgrade_date = (
            self.last_upgrade_date_entry.get_date() if self.last_upgrade_date_set_var.get() else None
        )
        contract_expiry_date = (
            self.contract_expiry_date_entry.get_date()
            if self.contract_expiry_date_set_var.get() else None
        )

        try:
            conn = get_connection()
            cursor = conn.cursor()

            if self.selected_id:
                cursor.execute(
                    """
                    UPDATE ControlSystems
                    SET UnitID = ?, SystemCode = ?, SystemName = ?, SystemType = ?,
                        Manufacturer = ?, Model = ?, SoftwareVersion = ?, FirmwareVersion = ?,
                        InstallDate = ?, CommissionDate = ?, LastUpgradeDate = ?,
                        RedundancyLevel = ?, CommunicationProtocol = ?, IsActive = ?,
                        MaintenanceContract = ?, ContractExpiryDate = ?
                    WHERE SystemID = ?
                    """,
                    (unit_id, system_code, system_name, system_type, manufacturer, model,
                     software_version, firmware_version, install_date, commission_date,
                     last_upgrade_date, redundancy_level, comm_protocol, is_active,
                     maintenance_contract, contract_expiry_date, self.selected_id)
                )
                conn.commit()
                messagebox.showinfo("Success", "Control System updated successfully.")
            else:
                cursor.execute(
                    """
                    INSERT INTO ControlSystems
                    (UnitID, SystemCode, SystemName, SystemType, Manufacturer, Model,
                     SoftwareVersion, FirmwareVersion, InstallDate, CommissionDate,
                     LastUpgradeDate, RedundancyLevel, CommunicationProtocol, IsActive,
                     MaintenanceContract, ContractExpiryDate)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (unit_id, system_code, system_name, system_type, manufacturer, model,
                     software_version, firmware_version, install_date, commission_date,
                     last_upgrade_date, redundancy_level, comm_protocol, is_active,
                     maintenance_contract, contract_expiry_date)
                )
                conn.commit()
                messagebox.showinfo("Success", "Control System added successfully.")

            conn.close()
            self.refresh_data()
            self._new_record()

        except pyodbc.IntegrityError as e:
            messagebox.showerror(
                "Integrity Error",
                f"Save failed. This likely violates a unique constraint "
                f"(System Code must be unique) or an invalid Process Unit reference:\n{e}"
            )
        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to save Control System:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error while saving:\n{e}")

    # ------------------------------------------------------------------
    # Delete (with dynamic FK dependency check)
    # ------------------------------------------------------------------
    def _get_dependent_records(self, conn, system_id):
        """
        Dynamically discover every table with a FK referencing ControlSystems,
        then count rows that reference this SystemID. This avoids hardcoding
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
                    (system_id,)
                )
                count = count_cursor.fetchone()[0]
                if count > 0:
                    dependents.append((child_table, count))
            except pyodbc.Error:
                continue

        return dependents

    def _delete_record(self):
        if not self.selected_id:
            messagebox.showwarning("No Selection", "Please select a Control System to delete.")
            return

        try:
            conn = get_connection()
            dependents = self._get_dependent_records(conn, self.selected_id)

            if dependents:
                detail = "\n".join(f"  - {table}: {count} record(s)" for table, count in dependents)
                proceed = messagebox.askyesno(
                    "Control System In Use",
                    f"This Control System is referenced by other records:\n\n{detail}\n\n"
                    "Deleting it may fail or orphan related data depending on your "
                    "database's FK constraints.\n\nDo you still want to attempt deletion?"
                )
                if not proceed:
                    conn.close()
                    return
            else:
                confirm = messagebox.askyesno(
                    "Confirm Delete",
                    f"Delete Control System '{self.system_name_var.get()}' (ID {self.selected_id})?"
                )
                if not confirm:
                    conn.close()
                    return

            cursor = conn.cursor()
            cursor.execute("DELETE FROM ControlSystems WHERE SystemID = ?", (self.selected_id,))
            conn.commit()
            conn.close()

            messagebox.showinfo("Deleted", "Control System deleted successfully.")
            self.refresh_data()
            self._new_record()

        except pyodbc.IntegrityError as e:
            messagebox.showerror(
                "Integrity Error",
                f"Cannot delete this Control System because other records depend on it:\n{e}"
            )
        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to delete Control System:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error while deleting:\n{e}")
