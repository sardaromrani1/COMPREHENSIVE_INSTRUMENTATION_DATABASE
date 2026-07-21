"""
SparePartUsage_form.py

CRUD form for the SparePartUsage table (tracks consumption of spare parts,
optionally tied to a maintenance work order).

    CREATE TABLE SparePartUsage (
        UsageID INT IDENTITY(1,1) PRIMARY KEY,
        SparePartID INT NOT NULL,
        Quantity INT NOT NULL,
        UsageDate DATE NOT NULL,
        WorkOrderNumber NVARCHAR(50),
        MaintenanceID INT,
        Notes NVARCHAR(500),
        FOREIGN KEY (SparePartID) REFERENCES SpareParts(SparePartID),
        FOREIGN KEY (MaintenanceID) REFERENCES MaintenanceRecords(MaintenanceID)
    );

Follows the same conventions as the other forms in this project:
    - get_connection() from db_connection (pyodbc / ODBC Driver 17 / Windows Auth)
    - FK comboboxes:
        SparePartID   -> SpareParts (PartNumber - PartName), required
        MaintenanceID -> MaintenanceRecords (WorkOrderNumber - Type - date), optional
    - UsageDate is DATE NOT NULL -> plain required DateEntry (no "Set" checkbox)
    - Quantity validated as a positive whole number
    - WorkOrderNumber here is a standalone free-text field (separate from the
      optional MaintenanceID link) since the DDL keeps both independently
    - pyodbc.IntegrityError caught separately for meaningful constraint messages
    - Dynamic FK-dependency check on delete using sys.foreign_keys
    - Column-scoped search / filter panel with live keyword filtering
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

import pyodbc
from tkcalendar import DateEntry

from db_connection import get_connection


class SparePartUsageForm(ttk.Frame):
    TABLE_NAME = "SparePartUsage"

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.selected_id = None
        self.sparepart_lookup = {}     # display string -> SparePartID
        self.maintenance_lookup = {}   # display string -> MaintenanceID

        self._build_ui()
        self._load_sparepart_lookup()
        self._load_maintenance_lookup()
        self.refresh_data()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------
    def _build_ui(self):
        # ---------------- Filter panel ----------------
        filter_frame = ttk.LabelFrame(self, text="Search / Filter")
        filter_frame.pack(side="top", fill="x", padx=8, pady=(8, 4))

        ttk.Label(filter_frame, text="Spare Part:").grid(row=0, column=0, sticky="w", padx=5, pady=4)
        self.sparepart_filter_var = tk.StringVar()
        self.sparepart_filter_combo = ttk.Combobox(
            filter_frame, textvariable=self.sparepart_filter_var, state="readonly", width=34
        )
        self.sparepart_filter_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=4)
        self.sparepart_filter_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_data())

        ttk.Label(filter_frame, text="Work Order #:").grid(row=0, column=2, sticky="w", padx=5, pady=4)
        self.search_text_var = tk.StringVar()
        search_entry = ttk.Entry(filter_frame, textvariable=self.search_text_var, width=22)
        search_entry.grid(row=0, column=3, sticky="ew", padx=5, pady=4)
        search_entry.bind("<KeyRelease>", lambda e: self.refresh_data())

        ttk.Label(filter_frame, text="Usage Date From:").grid(row=1, column=0, sticky="w", padx=5, pady=4)
        self.date_from = DateEntry(filter_frame, width=12, date_pattern="yyyy-mm-dd")
        self.date_from.grid(row=1, column=1, sticky="w", padx=5, pady=4)
        self.date_from_enabled = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            filter_frame, text="Use", variable=self.date_from_enabled, command=self.refresh_data
        ).grid(row=1, column=1, sticky="e", padx=5, pady=4)

        ttk.Label(filter_frame, text="Usage Date To:").grid(row=1, column=2, sticky="w", padx=5, pady=4)
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

        columns = ("UsageID", "SparePart", "Quantity", "UsageDate",
                   "WorkOrderNumber", "Maintenance")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=10)
        headings = {
            "UsageID": "ID", "SparePart": "Spare Part", "Quantity": "Qty",
            "UsageDate": "Usage Date", "WorkOrderNumber": "Work Order #",
            "Maintenance": "Maintenance Record",
        }
        widths = {
            "UsageID": 50, "SparePart": 220, "Quantity": 50, "UsageDate": 100,
            "WorkOrderNumber": 110, "Maintenance": 200,
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
        panel = ttk.LabelFrame(self, text="Spare Part Usage Details")
        panel.pack(side="top", fill="x", padx=8, pady=4)
        for col in range(4):
            panel.columnconfigure(col, weight=1)

        # UsageID (disabled, identity)
        ttk.Label(panel, text="Usage ID:").grid(row=0, column=0, sticky="w", padx=5, pady=4)
        self.id_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.id_var, width=20, state="disabled").grid(
            row=0, column=1, sticky="ew", padx=5, pady=4
        )

        # Spare Part (FK combobox, required)
        ttk.Label(panel, text="Spare Part *:").grid(row=0, column=2, sticky="w", padx=5, pady=4)
        self.sparepart_var = tk.StringVar()
        self.sparepart_combo = ttk.Combobox(
            panel, textvariable=self.sparepart_var, state="readonly", width=32
        )
        self.sparepart_combo.grid(row=0, column=3, sticky="ew", padx=5, pady=4)

        # Quantity (required)
        ttk.Label(panel, text="Quantity *:").grid(row=1, column=0, sticky="w", padx=5, pady=4)
        self.quantity_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.quantity_var, width=20).grid(
            row=1, column=1, sticky="ew", padx=5, pady=4
        )

        # UsageDate (required, not nullable)
        ttk.Label(panel, text="Usage Date *:").grid(row=1, column=2, sticky="w", padx=5, pady=4)
        self.usage_date_entry = DateEntry(panel, width=18, date_pattern="yyyy-mm-dd")
        self.usage_date_entry.grid(row=1, column=3, sticky="w", padx=5, pady=4)

        # WorkOrderNumber (free text, optional)
        ttk.Label(panel, text="Work Order Number:").grid(row=2, column=0, sticky="w", padx=5, pady=4)
        self.work_order_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.work_order_var, width=20).grid(
            row=2, column=1, sticky="ew", padx=5, pady=4
        )

        # Maintenance Record (FK combobox, optional)
        ttk.Label(panel, text="Maintenance Record:").grid(row=2, column=2, sticky="w", padx=5, pady=4)
        self.maintenance_var = tk.StringVar()
        self.maintenance_combo = ttk.Combobox(
            panel, textvariable=self.maintenance_var, state="readonly", width=32
        )
        self.maintenance_combo.grid(row=2, column=3, sticky="ew", padx=5, pady=4)

        # Notes (multi-line, 500 chars)
        ttk.Label(panel, text="Notes:").grid(row=3, column=0, sticky="nw", padx=5, pady=4)
        notes_frame = ttk.Frame(panel)
        notes_frame.grid(row=3, column=1, columnspan=3, sticky="ew", padx=5, pady=4)
        self.notes_text = tk.Text(notes_frame, height=3, width=50, wrap="word")
        notes_scroll = ttk.Scrollbar(notes_frame, orient="vertical", command=self.notes_text.yview)
        self.notes_text.configure(yscrollcommand=notes_scroll.set)
        self.notes_text.pack(side="left", fill="both", expand=True)
        notes_scroll.pack(side="right", fill="y")

        ttk.Label(panel, text="* Required fields", foreground="gray").grid(
            row=4, column=0, columnspan=2, sticky="w", padx=5, pady=4
        )

        # Action buttons
        action_frame = ttk.Frame(panel)
        action_frame.grid(row=5, column=0, columnspan=4, sticky="e", padx=5, pady=(10, 5))
        ttk.Button(action_frame, text="New", command=self._new_record).pack(side="left", padx=3)
        ttk.Button(action_frame, text="Save", command=self._save_record).pack(side="left", padx=3)
        ttk.Button(action_frame, text="Delete", command=self._delete_record).pack(side="left", padx=3)
        ttk.Button(action_frame, text="Refresh", command=self.refresh_data).pack(side="left", padx=3)
        ttk.Button(
            action_frame, text="Reload Lookups",
            command=lambda: (self._load_sparepart_lookup(), self._load_maintenance_lookup())
        ).pack(side="left", padx=3)

    def _clear_filter(self):
        self.sparepart_filter_var.set(
            "(All)" if "(All)" in self.sparepart_filter_combo["values"] else ""
        )
        self.search_text_var.set("")
        self.date_from_enabled.set(False)
        self.date_to_enabled.set(False)
        self.refresh_data()

    # ------------------------------------------------------------------
    # Spare Part FK lookup
    # ------------------------------------------------------------------
    def _load_sparepart_lookup(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT SparePartID, PartNumber, PartName
                FROM SpareParts
                ORDER BY PartNumber
                """
            )
            rows = cursor.fetchall()
            conn.close()

            self.sparepart_lookup = {}
            display_values = []
            for spare_part_id, part_number, part_name in rows:
                display = f"{part_number} - {part_name}" if part_name else part_number
                self.sparepart_lookup[display] = spare_part_id
                display_values.append(display)

            self.sparepart_combo["values"] = display_values
            self.sparepart_filter_combo["values"] = ["(All)"] + display_values
            if not self.sparepart_filter_var.get():
                self.sparepart_filter_var.set("(All)")

        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to load Spare Parts lookup:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error while loading Spare Parts:\n{e}")

    def _sparepart_display_for_id(self, spare_part_id):
        for display, spid in self.sparepart_lookup.items():
            if spid == spare_part_id:
                return display
        return f"[ID {spare_part_id}]"

    # ------------------------------------------------------------------
    # Maintenance Record FK lookup
    # ------------------------------------------------------------------
    def _load_maintenance_lookup(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT mr.MaintenanceID, i.TagNumber, mr.WorkOrderNumber,
                       mr.MaintenanceType, mr.CompletionDate
                FROM MaintenanceRecords mr
                LEFT JOIN Instruments i ON mr.InstrumentID = i.InstrumentID
                ORDER BY mr.CompletionDate DESC
                """
            )
            rows = cursor.fetchall()
            conn.close()

            self.maintenance_lookup = {}
            display_values = []
            for maintenance_id, tag_number, wo_number, maint_type, completion_date in rows:
                date_str = completion_date.strftime("%Y-%m-%d") if completion_date else "pending"
                display = (
                    f"{wo_number or ('MR #' + str(maintenance_id))} - "
                    f"{tag_number or 'Unknown'} ({maint_type or 'Unknown'}, {date_str})"
                )
                self.maintenance_lookup[display] = maintenance_id
                display_values.append(display)

            self.maintenance_combo["values"] = display_values

        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to load Maintenance Records lookup:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error while loading Maintenance Records:\n{e}")

    def _maintenance_display_for_id(self, maintenance_id):
        if maintenance_id is None:
            return ""
        for display, mid in self.maintenance_lookup.items():
            if mid == maintenance_id:
                return display
        return f"[ID {maintenance_id}]"

    # ------------------------------------------------------------------
    # Data loading / search
    # ------------------------------------------------------------------
    def refresh_data(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()

            query = """
                SELECT spu.UsageID, sp.PartNumber, sp.PartName, spu.Quantity,
                       spu.UsageDate, spu.WorkOrderNumber, mr.WorkOrderNumber, spu.MaintenanceID
                FROM SparePartUsage spu
                LEFT JOIN SpareParts sp ON spu.SparePartID = sp.SparePartID
                LEFT JOIN MaintenanceRecords mr ON spu.MaintenanceID = mr.MaintenanceID
                WHERE 1=1
            """
            params = []

            sparepart_display = self.sparepart_filter_var.get()
            if sparepart_display and sparepart_display != "(All)":
                spare_part_id = self.sparepart_lookup.get(sparepart_display)
                if spare_part_id is not None:
                    query += " AND spu.SparePartID = ?"
                    params.append(spare_part_id)

            keyword = self.search_text_var.get().strip()
            if keyword:
                query += " AND spu.WorkOrderNumber LIKE ?"
                params.append(f"%{keyword}%")

            if self.date_from_enabled.get():
                query += " AND spu.UsageDate >= ?"
                params.append(self.date_from.get_date())

            if self.date_to_enabled.get():
                query += " AND spu.UsageDate <= ?"
                params.append(self.date_to.get_date())

            query += " ORDER BY spu.UsageDate DESC"

            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()

            for item in self.tree.get_children():
                self.tree.delete(item)

            for row in rows:
                (usage_id, part_number, part_name, quantity, usage_date,
                 work_order_number, mr_work_order_number, maintenance_id) = row
                sparepart_label = f"{part_number} - {part_name}" if part_name else (part_number or "")
                maintenance_label = mr_work_order_number or (
                    f"MR #{maintenance_id}" if maintenance_id else ""
                )
                self.tree.insert(
                    "", "end", iid=str(usage_id),
                    values=(
                        usage_id, sparepart_label, quantity,
                        usage_date.strftime("%Y-%m-%d") if usage_date else "",
                        work_order_number or "", maintenance_label,
                    )
                )

        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to load Spare Part Usage data:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error while loading data:\n{e}")

    # ------------------------------------------------------------------
    # Selection / form population
    # ------------------------------------------------------------------
    def _on_select(self, event):
        selection = self.tree.selection()
        if not selection:
            return

        usage_id = int(selection[0])
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT UsageID, SparePartID, Quantity, UsageDate,
                       WorkOrderNumber, MaintenanceID, Notes
                FROM SparePartUsage
                WHERE UsageID = ?
                """,
                (usage_id,)
            )
            row = cursor.fetchone()
            conn.close()

            if not row:
                return

            (uid, spare_part_id, quantity, usage_date, work_order_number,
             maintenance_id, notes) = row

            self.selected_id = uid
            self.id_var.set(str(uid))
            self.sparepart_var.set(self._sparepart_display_for_id(spare_part_id))
            self.quantity_var.set(str(quantity) if quantity is not None else "")
            self.work_order_var.set(work_order_number or "")
            self.maintenance_var.set(self._maintenance_display_for_id(maintenance_id))

            if usage_date:
                self.usage_date_entry.set_date(usage_date)

            self.notes_text.delete("1.0", tk.END)
            if notes:
                self.notes_text.insert("1.0", notes)

        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to load Spare Part Usage record:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error while loading record:\n{e}")

    def _new_record(self):
        self.selected_id = None
        self.id_var.set("")
        self.sparepart_var.set("")
        self.quantity_var.set("")
        self.usage_date_entry.set_date(datetime.now())
        self.work_order_var.set("")
        self.maintenance_var.set("")
        self.notes_text.delete("1.0", tk.END)
        self.tree.selection_remove(self.tree.selection())

    # ------------------------------------------------------------------
    # Save (Insert / Update)
    # ------------------------------------------------------------------
    def _save_record(self):
        sparepart_display = self.sparepart_var.get().strip()
        if not sparepart_display:
            messagebox.showwarning("Validation", "Please select a Spare Part.")
            return

        spare_part_id = self.sparepart_lookup.get(sparepart_display)
        if spare_part_id is None:
            messagebox.showwarning("Validation", "Please select a valid Spare Part from the list.")
            return

        quantity_raw = self.quantity_var.get().strip()
        if not quantity_raw:
            messagebox.showwarning("Validation", "Please enter a Quantity.")
            return
        try:
            quantity = int(quantity_raw)
        except ValueError:
            messagebox.showwarning("Validation", "Quantity must be a whole number.")
            return
        if quantity <= 0:
            messagebox.showwarning("Validation", "Quantity must be greater than zero.")
            return

        usage_date = self.usage_date_entry.get_date()
        work_order_number = self.work_order_var.get().strip() or None

        maintenance_display = self.maintenance_var.get().strip()
        maintenance_id = self.maintenance_lookup.get(maintenance_display) if maintenance_display else None

        notes = self.notes_text.get("1.0", tk.END).strip() or None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            if self.selected_id:
                cursor.execute(
                    """
                    UPDATE SparePartUsage
                    SET SparePartID = ?, Quantity = ?, UsageDate = ?, WorkOrderNumber = ?,
                        MaintenanceID = ?, Notes = ?
                    WHERE UsageID = ?
                    """,
                    (spare_part_id, quantity, usage_date, work_order_number,
                     maintenance_id, notes, self.selected_id)
                )
                conn.commit()
                messagebox.showinfo("Success", "Spare Part Usage updated successfully.")
            else:
                cursor.execute(
                    """
                    INSERT INTO SparePartUsage
                    (SparePartID, Quantity, UsageDate, WorkOrderNumber, MaintenanceID, Notes)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (spare_part_id, quantity, usage_date, work_order_number, maintenance_id, notes)
                )
                conn.commit()
                messagebox.showinfo("Success", "Spare Part Usage added successfully.")

            conn.close()
            self.refresh_data()
            self._new_record()

        except pyodbc.IntegrityError as e:
            messagebox.showerror(
                "Integrity Error",
                f"Save failed. This likely indicates an invalid Spare Part or "
                f"Maintenance Record reference:\n{e}"
            )
        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to save Spare Part Usage:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error while saving:\n{e}")

    # ------------------------------------------------------------------
    # Delete (with dynamic FK dependency check)
    # ------------------------------------------------------------------
    def _get_dependent_records(self, conn, usage_id):
        """
        Dynamically discover every table with a FK referencing SparePartUsage,
        then count rows that reference this UsageID. Nothing references it
        today, but this keeps the form correct if that changes.
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
                    (usage_id,)
                )
                count = count_cursor.fetchone()[0]
                if count > 0:
                    dependents.append((child_table, count))
            except pyodbc.Error:
                continue

        return dependents

    def _delete_record(self):
        if not self.selected_id:
            messagebox.showwarning("No Selection", "Please select a Spare Part Usage record to delete.")
            return

        try:
            conn = get_connection()
            dependents = self._get_dependent_records(conn, self.selected_id)

            if dependents:
                detail = "\n".join(f"  - {table}: {count} record(s)" for table, count in dependents)
                proceed = messagebox.askyesno(
                    "Spare Part Usage In Use",
                    f"This Spare Part Usage record is referenced by other records:\n\n{detail}\n\n"
                    "Deleting it may fail or orphan related data depending on your "
                    "database's FK constraints.\n\nDo you still want to attempt deletion?"
                )
                if not proceed:
                    conn.close()
                    return
            else:
                confirm = messagebox.askyesno(
                    "Confirm Delete",
                    f"Delete this Spare Part Usage record (ID {self.selected_id})?"
                )
                if not confirm:
                    conn.close()
                    return

            cursor = conn.cursor()
            cursor.execute("DELETE FROM SparePartUsage WHERE UsageID = ?", (self.selected_id,))
            conn.commit()
            conn.close()

            messagebox.showinfo("Deleted", "Spare Part Usage record deleted successfully.")
            self.refresh_data()
            self._new_record()

        except pyodbc.IntegrityError as e:
            messagebox.showerror(
                "Integrity Error",
                f"Cannot delete this Spare Part Usage record because other records depend on it:\n{e}"
            )
        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to delete Spare Part Usage record:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error while deleting:\n{e}")
