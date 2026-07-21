"""
InstrumentLifecycle_form.py

CRUD form for the InstrumentLifecycle table (status history for Instruments).
Follows the same conventions as SubSystems_form.py:
    - get_connection() from db_connection (pyodbc / ODBC Driver 17 / Windows Auth)
    - FK combobox showing a human-readable label, storing the integer ID
    - Nullable dates handled with a "Set" checkbox + tkcalendar DateEntry
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


STATUS_CODES = ["Installed", "InService", "OutOfService", "Decommissioned"]


class InstrumentLifecycleForm(ttk.Frame):
    TABLE_NAME = "InstrumentLifecycle"

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.selected_id = None
        self.instrument_lookup = {} # display string -> InstrumentID

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

        ttk.Label(filter_frame, text="Status:").grid(row=0, column=2, sticky="w", padx=5, pady=4)
        self.status_filter_var = tk.StringVar()
        self.status_filter_combo = ttk.Combobox(
            filter_frame, textvariable=self.status_filter_var, state="readonly", width=18,
            values=["(All)"] + STATUS_CODES
        )
        self.status_filter_combo.set("(All)")
        self.status_filter_combo.grid(row=0, column=3, sticky="ew", padx=5, pady=4)
        self.status_filter_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_data())

        ttk.Label(filter_frame, text="Start Date From:").grid(row=1, column=0, sticky="w", padx=5, pady=4)
        self.date_from = DateEntry(filter_frame, width=12, date_pattern="yyyy-mm-dd")
        self.date_from.grid(row=1, column=1, sticky="w", padx=5, pady=4)
        self.date_from_enabled = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            filter_frame, text="Use", variable=self.date_from_enabled,
            command=self.refresh_data
        ).grid(row=1, column=1, sticky="e", padx=5, pady=4)

        ttk.Label(filter_frame, text="Start Date To:").grid(row=1, column=2, sticky="w", padx=5, pady=4)
        self.date_to = DateEntry(filter_frame, width=12, date_pattern="yyyy-mm-dd")
        self.date_to.grid(row=1, column=3, sticky="w", padx=5, pady=4)
        self.date_to_enabled = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            filter_frame, text="Use", variable=self.date_to_enabled,
            command=self.refresh_data
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

        columns = ("LifecycleID", "Instrument", "StatusCode", "StatusStartDate",
                   "StatusEndDate", "Reason", "ChangedBy")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=10)
        headings = {
            "LifecycleID": "ID",
            "Instrument": "Instrument",
            "StatusCode": "Status",
            "StatusStartDate": "Start Date",
            "StatusEndDate": "End Date",
            "Reason": "Reason",
            "ChangedBy": "Changed By",
        }
        widths = {
            "LifecycleID": 50, "Instrument": 220, "StatusCode": 100,
            "StatusStartDate": 100, "StatusEndDate": 100, "Reason": 200, "ChangedBy": 120,
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
        panel = ttk.LabelFrame(self, text="Lifecycle Record Details")
        panel.pack(side="top", fill="x", padx=8, pady=4)
        for col in range(4):
            panel.columnconfigure(col, weight=1)

        # LifecycleID (disabled, identity)
        ttk.Label(panel, text="Lifecycle ID:").grid(row=0, column=0, sticky="w", padx=5, pady=4)
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

        # StatusCode (required)
        ttk.Label(panel, text="Status Code *:").grid(row=1, column=0, sticky="w", padx=5, pady=4)
        self.status_var = tk.StringVar()
        self.status_combo = ttk.Combobox(
            panel, textvariable=self.status_var, state="readonly", width=20, values=STATUS_CODES
        )
        self.status_combo.grid(row=1, column=1, sticky="ew", padx=5, pady=4)

        # StatusStartDate (required, not nullable)
        ttk.Label(panel, text="Status Start Date *:").grid(row=1, column=2, sticky="w", padx=5, pady=4)
        self.start_date_entry = DateEntry(panel, width=18, date_pattern="yyyy-mm-dd")
        self.start_date_entry.grid(row=1, column=3, sticky="w", padx=5, pady=4)

        # StatusEndDate (nullable, with "Set" checkbox)
        ttk.Label(panel, text="Status End Date:").grid(row=2, column=0, sticky="w", padx=5, pady=4)
        end_date_frame = ttk.Frame(panel)
        end_date_frame.grid(row=2, column=1, sticky="w", padx=5, pady=4)
        self.end_date_set_var = tk.BooleanVar(value=False)
        self.end_date_entry = DateEntry(end_date_frame, width=15, date_pattern="yyyy-mm-dd", state="disabled")
        ttk.Checkbutton(
            end_date_frame, text="Set", variable=self.end_date_set_var,
            command=self._toggle_end_date
        ).pack(side="left")
        self.end_date_entry.pack(side="left", padx=(5, 0))

        # Reason
        ttk.Label(panel, text="Reason:").grid(row=2, column=2, sticky="w", padx=5, pady=4)
        self.reason_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.reason_var, width=32).grid(
            row=2, column=3, sticky="ew", padx=5, pady=4
        )

        # ChangedBy
        ttk.Label(panel, text="Changed By:").grid(row=3, column=0, sticky="w", padx=5, pady=4)
        self.changed_by_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.changed_by_var, width=20).grid(
            row=3, column=1, sticky="ew", padx=5, pady=4
        )

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
        ttk.Button(action_frame, text="Reload Instruments", command=self._load_instrument_lookup).pack(
            side="left", padx=3
        )

    def _toggle_end_date(self):
        if self.end_date_set_var.get():
            self.end_date_entry.configure(state="normal")
        else:
            self.end_date_entry.configure(state="disabled")

    def _clear_filter(self):
        self.instrument_filter_var.set("(All)" if "(All)" in self.instrument_filter_combo["values"] else "")
        self.status_filter_combo.set("(All)")
        self.date_from_enabled.set(False)
        self.date_to_enabled.set(False)
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
                SELECT il.LifecycleID, il.InstrumentID, i.TagNumber, i.Description,
                       il.StatusCode, il.StatusStartDate, il.StatusEndDate,
                       il.Reason, il.ChangedBy
                FROM InstrumentLifecycle il
                LEFT JOIN Instruments i ON il.InstrumentID = i.InstrumentID
                WHERE 1=1
            """
            params = []

            instrument_display = self.instrument_filter_var.get()
            if instrument_display and instrument_display != "(All)":
                instrument_id = self.instrument_lookup.get(instrument_display)
                if instrument_id is not None:
                    query += " AND il.InstrumentID = ?"
                    params.append(instrument_id)

            status_filter = self.status_filter_var.get()
            if status_filter and status_filter != "(All)":
                query += " AND il.StatusCode = ?"
                params.append(status_filter)

            if self.date_from_enabled.get():
                query += " AND il.StatusStartDate >= ?"
                params.append(self.date_from.get_date())

            if self.date_to_enabled.get():
                query += " AND il.StatusStartDate <= ?"
                params.append(self.date_to.get_date())

            query += " ORDER BY il.StatusStartDate DESC"

            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()

            for item in self.tree.get_children():
                self.tree.delete(item)

            for row in rows:
                (lifecycle_id, instrument_id, tag_number, description,
                 status_code, start_date, end_date, reason, changed_by) = row
                instrument_label = f"{tag_number} - {description}" if description else (tag_number or "")
                self.tree.insert(
                    "", "end", iid=str(lifecycle_id),
                    values=(
                        lifecycle_id,
                        instrument_label,
                        status_code,
                        start_date.strftime("%Y-%m-%d") if start_date else "",
                        end_date.strftime("%Y-%m-%d") if end_date else "",
                        reason or "",
                        changed_by or "",
                    )
                )

        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to load Instrument Lifecycle data:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error while loading data:\n{e}")

    # ------------------------------------------------------------------
    # Selection / form population
    # ------------------------------------------------------------------
    def _on_select(self, event):
        selection = self.tree.selection()
        if not selection:
            return

        lifecycle_id = int(selection[0])
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT LifecycleID, InstrumentID, StatusCode, StatusStartDate,
                       StatusEndDate, Reason, ChangedBy
                FROM InstrumentLifecycle
                WHERE LifecycleID = ?
                """,
                (lifecycle_id,)
            )
            row = cursor.fetchone()
            conn.close()

            if not row:
                return

            (lc_id, instrument_id, status_code, start_date, end_date, reason, changed_by) = row

            self.selected_id = lc_id
            self.id_var.set(str(lc_id))
            self.instrument_var.set(self._instrument_display_for_id(instrument_id))
            self.status_var.set(status_code or "")

            if start_date:
                self.start_date_entry.set_date(start_date)

            if end_date:
                self.end_date_set_var.set(True)
                self.end_date_entry.configure(state="normal")
                self.end_date_entry.set_date(end_date)
            else:
                self.end_date_set_var.set(False)
                self.end_date_entry.configure(state="disabled")

            self.reason_var.set(reason or "")
            self.changed_by_var.set(changed_by or "")

        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to load Lifecycle record:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error while loading record:\n{e}")

    def _new_record(self):
        self.selected_id = None
        self.id_var.set("")
        self.instrument_var.set("")
        self.status_var.set("")
        self.start_date_entry.set_date(datetime.now())
        self.end_date_set_var.set(False)
        self.end_date_entry.configure(state="disabled")
        self.reason_var.set("")
        self.changed_by_var.set("")
        self.tree.selection_remove(self.tree.selection())

    # ------------------------------------------------------------------
    # Save (Insert / Update)
    # ------------------------------------------------------------------
    def _save_record(self):
        instrument_display = self.instrument_var.get().strip()
        status_code = self.status_var.get().strip()

        if not instrument_display:
            messagebox.showwarning("Validation", "Please select an Instrument.")
            return
        if not status_code:
            messagebox.showwarning("Validation", "Please select a Status Code.")
            return

        instrument_id = self.instrument_lookup.get(instrument_display)
        if instrument_id is None:
            messagebox.showwarning("Validation", "Please select a valid Instrument from the list.")
            return

        start_date = self.start_date_entry.get_date()
        end_date = self.end_date_entry.get_date() if self.end_date_set_var.get() else None
        reason = self.reason_var.get().strip() or None
        changed_by = self.changed_by_var.get().strip() or None

        if end_date and end_date < start_date:
            messagebox.showwarning("Validation", "Status End Date cannot be before Status Start Date.")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()

            if self.selected_id:
                cursor.execute(
                    """
                    UPDATE InstrumentLifecycle
                    SET InstrumentID = ?, StatusCode = ?, StatusStartDate = ?,
                        StatusEndDate = ?, Reason = ?, ChangedBy = ?
                    WHERE LifecycleID = ?
                    """,
                    (instrument_id, status_code, start_date, end_date, reason, changed_by,
                     self.selected_id)
                )
                conn.commit()
                messagebox.showinfo("Success", "Lifecycle record updated successfully.")
            else:
                cursor.execute(
                    """
                    INSERT INTO InstrumentLifecycle
                    (InstrumentID, StatusCode, StatusStartDate, StatusEndDate, Reason, ChangedBy)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (instrument_id, status_code, start_date, end_date, reason, changed_by)
                )
                conn.commit()
                messagebox.showinfo("Success", "Lifecycle record added successfully.")

            conn.close()
            self.refresh_data()
            self._new_record()

        except pyodbc.IntegrityError as e:
            messagebox.showerror(
                "Integrity Error",
                f"Save failed. This likely indicates an invalid Instrument reference:\n{e}"
            )
        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to save Lifecycle record:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error while saving:\n{e}")

    # ------------------------------------------------------------------
    # Delete (with dynamic FK dependency check)
    # ------------------------------------------------------------------
    def _get_dependent_records(self, conn, lifecycle_id):
        """
        Dynamically discover every table with a FK referencing InstrumentLifecycle,
        then count rows that reference this LifecycleID. Nothing references it
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
                    (lifecycle_id,)
                )
                count = count_cursor.fetchone()[0]
                if count > 0:
                    dependents.append((child_table, count))
            except pyodbc.Error:
                continue

        return dependents

    def _delete_record(self):
        if not self.selected_id:
            messagebox.showwarning("No Selection", "Please select a Lifecycle record to delete.")
            return

        try:
            conn = get_connection()
            dependents = self._get_dependent_records(conn, self.selected_id)

            if dependents:
                detail = "\n".join(f" - {table}: {count} record(s)" for table, count in dependents)
                proceed = messagebox.askyesno(
                    "Lifecycle Record In Use",
                    f"This Lifecycle record is referenced by other records:\n\n{detail}\n\n"
                    "Deleting it may fail or orphan related data depending on your "
                    "database's FK constraints.\n\nDo you still want to attempt deletion?"
                )
                if not proceed:
                    conn.close()
                    return
            else:
                confirm = messagebox.askyesno(
                    "Confirm Delete",
                    f"Delete this Lifecycle record (ID {self.selected_id})?"
                )
                if not confirm:
                    conn.close()
                    return

            cursor = conn.cursor()
            cursor.execute("DELETE FROM InstrumentLifecycle WHERE LifecycleID = ?", (self.selected_id,))
            conn.commit()
            conn.close()

            messagebox.showinfo("Deleted", "Lifecycle record deleted successfully.")
            self.refresh_data()
            self._new_record()

        except pyodbc.IntegrityError as e:
            messagebox.showerror(
                "Integrity Error",
                f"Cannot delete this Lifecycle record because other records depend on it:\n{e}"
            )
        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to delete Lifecycle record:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error while deleting:\n{e}")
