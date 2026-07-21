"""
InstrumentTypes_form.py

CRUD form for the InstrumentTypes table.

Follows the same conventions as the other forms in this project:
    - get_connection() from db_connection (pyodbc / ODBC Driver 17 / Windows Auth)
    - Identity PK (InstrumentTypeID) shown disabled
    - BIT columns rendered as checkbuttons
    - pyodbc.IntegrityError caught separately for meaningful constraint messages
    - Dynamic FK-dependency check on delete using sys.foreign_keys
    - Column-scoped search / filter panel with live keyword filtering
"""

import tkinter as tk
from tkinter import ttk, messagebox

import pyodbc

from db_connection import get_connection


class InstrumentTypesForm(ttk.Frame):
    TABLE_NAME = "InstrumentTypes"

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.selected_id = None

        self._build_ui()
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
            values=["(All Columns)", "TypeCode", "TypeName", "Category",
                    "SubCategory", "MeasurementPrinciple"]
        )
        self.search_column_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=4)

        ttk.Label(filter_frame, text="Keyword:").grid(row=0, column=2, sticky="w", padx=5, pady=4)
        self.search_text_var = tk.StringVar()
        search_entry = ttk.Entry(filter_frame, textvariable=self.search_text_var, width=28)
        search_entry.grid(row=0, column=3, sticky="ew", padx=5, pady=4)
        search_entry.bind("<KeyRelease>", lambda e: self.refresh_data())

        ttk.Label(filter_frame, text="Category:").grid(row=1, column=0, sticky="w", padx=5, pady=4)
        self.category_filter_var = tk.StringVar(value="(All)")
        self.category_filter_combo = ttk.Combobox(
            filter_frame, textvariable=self.category_filter_var, state="readonly", width=20,
            values=["(All)", "Measurement", "Control", "Safety", "Analyzer", "Actuator"]
        )
        self.category_filter_combo.grid(row=1, column=1, sticky="ew", padx=5, pady=4)
        self.category_filter_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_data())

        btn_frame = ttk.Frame(filter_frame)
        btn_frame.grid(row=2, column=0, columnspan=4, sticky="w", padx=5, pady=(0, 4))
        ttk.Button(btn_frame, text="Apply Filter", command=self.refresh_data).pack(side="left", padx=3)
        ttk.Button(btn_frame, text="Clear Filter", command=self._clear_filter).pack(side="left", padx=3)

        for col in range(4):
            filter_frame.columnconfigure(col, weight=1)

        # ---------------- Treeview ----------------
        tree_frame = ttk.Frame(self)
        tree_frame.pack(side="top", fill="both", expand=True, padx=8, pady=4)

        columns = ("InstrumentTypeID", "TypeCode", "TypeName", "Category",
                   "SubCategory", "MeasurementPrinciple", "StandardCalibrationInterval")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=10)
        headings = {
            "InstrumentTypeID": "ID",
            "TypeCode": "Type Code",
            "TypeName": "Type Name",
            "Category": "Category",
            "SubCategory": "Sub-Category",
            "MeasurementPrinciple": "Measurement Principle",
            "StandardCalibrationInterval": "Cal. Interval (days)",
        }
        widths = {
            "InstrumentTypeID": 50, "TypeCode": 90, "TypeName": 160, "Category": 100,
            "SubCategory": 100, "MeasurementPrinciple": 160, "StandardCalibrationInterval": 120,
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
        panel = ttk.LabelFrame(self, text="Instrument Type Details")
        panel.pack(side="top", fill="x", padx=8, pady=4)
        for col in range(4):
            panel.columnconfigure(col, weight=1)

        # InstrumentTypeID (disabled, identity)
        ttk.Label(panel, text="Type ID:").grid(row=0, column=0, sticky="w", padx=5, pady=4)
        self.id_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.id_var, width=20, state="disabled").grid(
            row=0, column=1, sticky="ew", padx=5, pady=4
        )

        # TypeCode (required, unique)
        ttk.Label(panel, text="Type Code *:").grid(row=0, column=2, sticky="w", padx=5, pady=4)
        self.type_code_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.type_code_var, width=20).grid(
            row=0, column=3, sticky="ew", padx=5, pady=4
        )

        # TypeName (required)
        ttk.Label(panel, text="Type Name *:").grid(row=1, column=0, sticky="w", padx=5, pady=4)
        self.type_name_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.type_name_var, width=28).grid(
            row=1, column=1, sticky="ew", padx=5, pady=4
        )

        # Category
        ttk.Label(panel, text="Category:").grid(row=1, column=2, sticky="w", padx=5, pady=4)
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(
            panel, textvariable=self.category_var, width=26,
            values=["Measurement", "Control", "Safety", "Analyzer", "Actuator"]
        )
        self.category_combo.grid(row=1, column=3, sticky="ew", padx=5, pady=4)

        # SubCategory
        ttk.Label(panel, text="Sub-Category:").grid(row=2, column=0, sticky="w", padx=5, pady=4)
        self.sub_category_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.sub_category_var, width=20).grid(
            row=2, column=1, sticky="ew", padx=5, pady=4
        )

        # MeasurementPrinciple
        ttk.Label(panel, text="Measurement Principle:").grid(row=2, column=2, sticky="w", padx=5, pady=4)
        self.measurement_principle_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.measurement_principle_var, width=26).grid(
            row=2, column=3, sticky="ew", padx=5, pady=4
        )

        # StandardCalibrationInterval
        ttk.Label(panel, text="Std. Cal. Interval (days):").grid(row=3, column=0, sticky="w", padx=5, pady=4)
        self.cal_interval_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.cal_interval_var, width=20).grid(
            row=3, column=1, sticky="ew", padx=5, pady=4
        )

        # TypicalAccuracy
        ttk.Label(panel, text="Typical Accuracy:").grid(row=3, column=2, sticky="w", padx=5, pady=4)
        self.typical_accuracy_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.typical_accuracy_var, width=26).grid(
            row=3, column=3, sticky="ew", padx=5, pady=4
        )

        # TypicalRangeability
        ttk.Label(panel, text="Typical Rangeability:").grid(row=4, column=0, sticky="w", padx=5, pady=4)
        self.typical_rangeability_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.typical_rangeability_var, width=20).grid(
            row=4, column=1, sticky="ew", padx=5, pady=4
        )

        # Checkbuttons: RequiresCertification, RequiresFunctionalTest, IsExplosionProof
        check_frame = ttk.Frame(panel)
        check_frame.grid(row=5, column=0, columnspan=4, sticky="w", padx=5, pady=4)

        self.requires_certification_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            check_frame, text="Requires Certification", variable=self.requires_certification_var
        ).pack(side="left", padx=(0, 15))

        self.requires_functional_test_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            check_frame, text="Requires Functional Test", variable=self.requires_functional_test_var
        ).pack(side="left", padx=(0, 15))

        self.is_explosion_proof_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            check_frame, text="Explosion Proof", variable=self.is_explosion_proof_var
        ).pack(side="left")

        # Description (multi-line, 500 chars)
        ttk.Label(panel, text="Description:").grid(row=6, column=0, sticky="nw", padx=5, pady=4)
        desc_frame = ttk.Frame(panel)
        desc_frame.grid(row=6, column=1, columnspan=3, sticky="ew", padx=5, pady=4)
        self.description_text = tk.Text(desc_frame, height=4, width=50, wrap="word")
        desc_scroll = ttk.Scrollbar(desc_frame, orient="vertical", command=self.description_text.yview)
        self.description_text.configure(yscrollcommand=desc_scroll.set)
        self.description_text.pack(side="left", fill="both", expand=True)
        desc_scroll.pack(side="right", fill="y")

        ttk.Label(panel, text="* Required fields", foreground="gray").grid(
            row=7, column=0, columnspan=2, sticky="w", padx=5, pady=4
        )

        # Action buttons
        action_frame = ttk.Frame(panel)
        action_frame.grid(row=8, column=0, columnspan=4, sticky="e", padx=5, pady=(10, 5))
        ttk.Button(action_frame, text="New", command=self._new_record).pack(side="left", padx=3)
        ttk.Button(action_frame, text="Save", command=self._save_record).pack(side="left", padx=3)
        ttk.Button(action_frame, text="Delete", command=self._delete_record).pack(side="left", padx=3)
        ttk.Button(action_frame, text="Refresh", command=self.refresh_data).pack(side="left", padx=3)

    def _clear_filter(self):
        self.search_column_var.set("(All Columns)")
        self.search_text_var.set("")
        self.category_filter_var.set("(All)")
        self.refresh_data()

    # ------------------------------------------------------------------
    # Data loading / search
    # ------------------------------------------------------------------
    def refresh_data(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()

            query = """
                SELECT InstrumentTypeID, TypeCode, TypeName, Category,
                       SubCategory, MeasurementPrinciple, StandardCalibrationInterval
                FROM InstrumentTypes
                WHERE 1=1
            """
            params = []

            keyword = self.search_text_var.get().strip()
            if keyword:
                column = self.search_column_var.get()
                like_value = f"%{keyword}%"
                searchable_columns = ["TypeCode", "TypeName", "Category",
                                      "SubCategory", "MeasurementPrinciple"]
                if column in searchable_columns:
                    query += f" AND {column} LIKE ?"
                    params.append(like_value)
                else:
                    conditions = " OR ".join(f"{c} LIKE ?" for c in searchable_columns)
                    query += f" AND ({conditions})"
                    params.extend([like_value] * len(searchable_columns))

            category_filter = self.category_filter_var.get()
            if category_filter and category_filter != "(All)":
                query += " AND Category = ?"
                params.append(category_filter)

            query += " ORDER BY TypeCode"

            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()

            for item in self.tree.get_children():
                self.tree.delete(item)

            for row in rows:
                (type_id, type_code, type_name, category, sub_category,
                 measurement_principle, cal_interval) = row
                self.tree.insert(
                    "", "end", iid=str(type_id),
                    values=(
                        type_id, type_code, type_name, category or "",
                        sub_category or "", measurement_principle or "",
                        cal_interval if cal_interval is not None else "",
                    )
                )

        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to load Instrument Types data:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error while loading data:\n{e}")

    # ------------------------------------------------------------------
    # Selection / form population
    # ------------------------------------------------------------------
    def _on_select(self, event):
        selection = self.tree.selection()
        if not selection:
            return

        type_id = int(selection[0])
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT InstrumentTypeID, TypeCode, TypeName, Category, SubCategory,
                       Description, MeasurementPrinciple, StandardCalibrationInterval,
                       RequiresCertification, RequiresFunctionalTest, IsExplosionProof,
                       TypicalAccuracy, TypicalRangeability
                FROM InstrumentTypes
                WHERE InstrumentTypeID = ?
                """,
                (type_id,)
            )
            row = cursor.fetchone()
            conn.close()

            if not row:
                return

            (tid, type_code, type_name, category, sub_category, description,
             measurement_principle, cal_interval, requires_certification,
             requires_functional_test, is_explosion_proof, typical_accuracy,
             typical_rangeability) = row

            self.selected_id = tid
            self.id_var.set(str(tid))
            self.type_code_var.set(type_code or "")
            self.type_name_var.set(type_name or "")
            self.category_var.set(category or "")
            self.sub_category_var.set(sub_category or "")
            self.measurement_principle_var.set(measurement_principle or "")
            self.cal_interval_var.set(str(cal_interval) if cal_interval is not None else "")
            self.typical_accuracy_var.set(typical_accuracy or "")
            self.typical_rangeability_var.set(typical_rangeability or "")
            self.requires_certification_var.set(bool(requires_certification))
            self.requires_functional_test_var.set(bool(requires_functional_test))
            self.is_explosion_proof_var.set(bool(is_explosion_proof))

            self.description_text.delete("1.0", tk.END)
            if description:
                self.description_text.insert("1.0", description)

        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to load Instrument Type record:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error while loading record:\n{e}")

    def _new_record(self):
        self.selected_id = None
        self.id_var.set("")
        self.type_code_var.set("")
        self.type_name_var.set("")
        self.category_var.set("")
        self.sub_category_var.set("")
        self.measurement_principle_var.set("")
        self.cal_interval_var.set("")
        self.typical_accuracy_var.set("")
        self.typical_rangeability_var.set("")
        self.requires_certification_var.set(False)
        self.requires_functional_test_var.set(False)
        self.is_explosion_proof_var.set(False)
        self.description_text.delete("1.0", tk.END)
        self.tree.selection_remove(self.tree.selection())

    # ------------------------------------------------------------------
    # Save (Insert / Update)
    # ------------------------------------------------------------------
    def _save_record(self):
        type_code = self.type_code_var.get().strip()
        type_name = self.type_name_var.get().strip()

        if not type_code:
            messagebox.showwarning("Validation", "Please enter a Type Code.")
            return
        if not type_name:
            messagebox.showwarning("Validation", "Please enter a Type Name.")
            return

        cal_interval_raw = self.cal_interval_var.get().strip()
        cal_interval = None
        if cal_interval_raw:
            try:
                cal_interval = int(cal_interval_raw)
            except ValueError:
                messagebox.showwarning(
                    "Validation", "Standard Calibration Interval must be a whole number of days."
                )
                return

        category = self.category_var.get().strip() or None
        sub_category = self.sub_category_var.get().strip() or None
        measurement_principle = self.measurement_principle_var.get().strip() or None
        typical_accuracy = self.typical_accuracy_var.get().strip() or None
        typical_rangeability = self.typical_rangeability_var.get().strip() or None
        description = self.description_text.get("1.0", tk.END).strip() or None

        requires_certification = self.requires_certification_var.get()
        requires_functional_test = self.requires_functional_test_var.get()
        is_explosion_proof = self.is_explosion_proof_var.get()

        try:
            conn = get_connection()
            cursor = conn.cursor()

            if self.selected_id:
                cursor.execute(
                    """
                    UPDATE InstrumentTypes
                    SET TypeCode = ?, TypeName = ?, Category = ?, SubCategory = ?,
                        Description = ?, MeasurementPrinciple = ?, StandardCalibrationInterval = ?,
                        RequiresCertification = ?, RequiresFunctionalTest = ?, IsExplosionProof = ?,
                        TypicalAccuracy = ?, TypicalRangeability = ?
                    WHERE InstrumentTypeID = ?
                    """,
                    (type_code, type_name, category, sub_category, description,
                     measurement_principle, cal_interval, requires_certification,
                     requires_functional_test, is_explosion_proof, typical_accuracy,
                     typical_rangeability, self.selected_id)
                )
                conn.commit()
                messagebox.showinfo("Success", "Instrument Type updated successfully.")
            else:
                cursor.execute(
                    """
                    INSERT INTO InstrumentTypes
                    (TypeCode, TypeName, Category, SubCategory, Description,
                     MeasurementPrinciple, StandardCalibrationInterval,
                     RequiresCertification, RequiresFunctionalTest, IsExplosionProof,
                     TypicalAccuracy, TypicalRangeability)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (type_code, type_name, category, sub_category, description,
                     measurement_principle, cal_interval, requires_certification,
                     requires_functional_test, is_explosion_proof, typical_accuracy,
                     typical_rangeability)
                )
                conn.commit()
                messagebox.showinfo("Success", "Instrument Type added successfully.")

            conn.close()
            self.refresh_data()
            self._new_record()

        except pyodbc.IntegrityError as e:
            messagebox.showerror(
                "Integrity Error",
                f"Save failed. This likely violates a unique constraint "
                f"(Type Code must be unique):\n{e}"
            )
        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to save Instrument Type:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error while saving:\n{e}")

    # ------------------------------------------------------------------
    # Delete (with dynamic FK dependency check)
    # ------------------------------------------------------------------
    def _get_dependent_records(self, conn, type_id):
        """
        Dynamically discover every table with a FK referencing InstrumentTypes,
        then count rows that reference this InstrumentTypeID. This avoids
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
                    (type_id,)
                )
                count = count_cursor.fetchone()[0]
                if count > 0:
                    dependents.append((child_table, count))
            except pyodbc.Error:
                continue

        return dependents

    def _delete_record(self):
        if not self.selected_id:
            messagebox.showwarning("No Selection", "Please select an Instrument Type to delete.")
            return

        try:
            conn = get_connection()
            dependents = self._get_dependent_records(conn, self.selected_id)

            if dependents:
                detail = "\n".join(f"  - {table}: {count} record(s)" for table, count in dependents)
                proceed = messagebox.askyesno(
                    "Instrument Type In Use",
                    f"This Instrument Type is referenced by other records:\n\n{detail}\n\n"
                    "Deleting it may fail or orphan related data depending on your "
                    "database's FK constraints.\n\nDo you still want to attempt deletion?"
                )
                if not proceed:
                    conn.close()
                    return
            else:
                confirm = messagebox.askyesno(
                    "Confirm Delete",
                    f"Delete Instrument Type '{self.type_name_var.get()}' (ID {self.selected_id})?"
                )
                if not confirm:
                    conn.close()
                    return

            cursor = conn.cursor()
            cursor.execute("DELETE FROM InstrumentTypes WHERE InstrumentTypeID = ?", (self.selected_id,))
            conn.commit()
            conn.close()

            messagebox.showinfo("Deleted", "Instrument Type deleted successfully.")
            self.refresh_data()
            self._new_record()

        except pyodbc.IntegrityError as e:
            messagebox.showerror(
                "Integrity Error",
                f"Cannot delete this Instrument Type because other records depend on it:\n{e}"
            )
        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to delete Instrument Type:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error while deleting:\n{e}")
