"""
CalibrationTestPoints_form.py

CRUD form for the CalibrationTestPoints table (child of CalibrationRecords -
one row per test point within a calibration run).

    CREATE TABLE CalibrationTestPoints (
        TestPointID INT PRIMARY KEY IDENTITY(1,1),
        CalibrationID INT NOT NULL,
        TestSequence INT,
        AppliedInput DECIMAL(18,4),
        AsFoundOutput DECIMAL(18,4),
        AsLeftOutput DECIMAL(18,4),
        ExpectedOutput DECIMAL(18,4),
        AsFoundError DECIMAL(18,4),
        AsFoundError_Percent DECIMAL(5,2),
        AsLeftError DECIMAL(18,4),
        AsLeftError_Percent DECIMAL(5,2),
        IsWithinTolerance BIT,
        FOREIGN KEY (CalibrationID) REFERENCES CalibrationRecords(CalibrationID)
    );

Follows the same conventions as the other forms in this project:
    - get_connection() from db_connection (pyodbc / ODBC Driver 17 / Windows Auth)
    - FK combobox (CalibrationID -> CalibrationRecords, joined through
      Instruments for a readable label) showing a human-readable label,
      storing the integer ID
    - IsWithinTolerance is a nullable BIT (no DEFAULT in the DDL), so it's
      rendered as a tri-state combobox: (Not Set) / Yes / No, rather than a
      plain checkbutton which can only represent True/False
    - pyodbc.IntegrityError caught separately for meaningful constraint messages
    - Dynamic FK-dependency check on delete using sys.foreign_keys
    - Column-scoped search / filter panel with live keyword filtering
"""

import tkinter as tk
from tkinter import ttk, messagebox

import pyodbc

from db_connection import get_connection


TRISTATE_VALUES = ["(Not Set)", "Yes", "No"]


class CalibrationTestPointsForm(ttk.Frame):
    TABLE_NAME = "CalibrationTestPoints"

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.selected_id = None
        self.calibration_lookup = {}   # display string -> CalibrationID

        self._build_ui()
        self._load_calibration_lookup()
        self.refresh_data()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------
    def _build_ui(self):
        # ---------------- Filter panel ----------------
        filter_frame = ttk.LabelFrame(self, text="Search / Filter")
        filter_frame.pack(side="top", fill="x", padx=8, pady=(8, 4))

        ttk.Label(filter_frame, text="Calibration Record:").grid(
            row=0, column=0, sticky="w", padx=5, pady=4
        )
        self.calibration_filter_var = tk.StringVar()
        self.calibration_filter_combo = ttk.Combobox(
            filter_frame, textvariable=self.calibration_filter_var, state="readonly", width=40
        )
        self.calibration_filter_combo.grid(row=0, column=1, columnspan=2, sticky="ew", padx=5, pady=4)
        self.calibration_filter_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_data())

        ttk.Label(filter_frame, text="Within Tolerance:").grid(
            row=0, column=3, sticky="w", padx=5, pady=4
        )
        self.tolerance_filter_var = tk.StringVar(value="(All)")
        self.tolerance_filter_combo = ttk.Combobox(
            filter_frame, textvariable=self.tolerance_filter_var, state="readonly", width=14,
            values=["(All)"] + TRISTATE_VALUES[1:]
        )
        self.tolerance_filter_combo.grid(row=0, column=4, sticky="ew", padx=5, pady=4)
        self.tolerance_filter_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_data())

        btn_frame = ttk.Frame(filter_frame)
        btn_frame.grid(row=1, column=0, columnspan=5, sticky="w", padx=5, pady=(0, 4))
        ttk.Button(btn_frame, text="Apply Filter", command=self.refresh_data).pack(side="left", padx=3)
        ttk.Button(btn_frame, text="Clear Filter", command=self._clear_filter).pack(side="left", padx=3)

        for col in range(5):
            filter_frame.columnconfigure(col, weight=1)

        # ---------------- Treeview ----------------
        tree_frame = ttk.Frame(self)
        tree_frame.pack(side="top", fill="both", expand=True, padx=8, pady=4)

        columns = ("TestPointID", "Calibration", "TestSequence", "AppliedInput",
                   "AsFoundOutput", "AsLeftOutput", "ExpectedOutput", "IsWithinTolerance")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=10)
        headings = {
            "TestPointID": "ID", "Calibration": "Calibration Record", "TestSequence": "Seq",
            "AppliedInput": "Applied Input", "AsFoundOutput": "As-Found Output",
            "AsLeftOutput": "As-Left Output", "ExpectedOutput": "Expected Output",
            "IsWithinTolerance": "Within Tol.",
        }
        widths = {
            "TestPointID": 50, "Calibration": 220, "TestSequence": 50,
            "AppliedInput": 100, "AsFoundOutput": 110, "AsLeftOutput": 100,
            "ExpectedOutput": 110, "IsWithinTolerance": 80,
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
        panel = ttk.LabelFrame(self, text="Test Point Details")
        panel.pack(side="top", fill="x", padx=8, pady=4)
        for col in range(4):
            panel.columnconfigure(col, weight=1)

        # TestPointID (disabled, identity)
        ttk.Label(panel, text="Test Point ID:").grid(row=0, column=0, sticky="w", padx=5, pady=4)
        self.id_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.id_var, width=20, state="disabled").grid(
            row=0, column=1, sticky="ew", padx=5, pady=4
        )

        # Calibration Record (FK combobox, required)
        ttk.Label(panel, text="Calibration Record *:").grid(row=0, column=2, sticky="w", padx=5, pady=4)
        self.calibration_var = tk.StringVar()
        self.calibration_combo = ttk.Combobox(
            panel, textvariable=self.calibration_var, state="readonly", width=32
        )
        self.calibration_combo.grid(row=0, column=3, sticky="ew", padx=5, pady=4)

        # TestSequence
        ttk.Label(panel, text="Test Sequence:").grid(row=1, column=0, sticky="w", padx=5, pady=4)
        self.test_sequence_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.test_sequence_var, width=20).grid(
            row=1, column=1, sticky="ew", padx=5, pady=4
        )

        # IsWithinTolerance (tri-state, nullable BIT)
        ttk.Label(panel, text="Within Tolerance:").grid(row=1, column=2, sticky="w", padx=5, pady=4)
        self.within_tolerance_var = tk.StringVar(value="(Not Set)")
        ttk.Combobox(
            panel, textvariable=self.within_tolerance_var, state="readonly", width=26,
            values=TRISTATE_VALUES
        ).grid(row=1, column=3, sticky="ew", padx=5, pady=4)

        # AppliedInput / ExpectedOutput
        ttk.Label(panel, text="Applied Input:").grid(row=2, column=0, sticky="w", padx=5, pady=4)
        self.applied_input_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.applied_input_var, width=20).grid(
            row=2, column=1, sticky="ew", padx=5, pady=4
        )

        ttk.Label(panel, text="Expected Output:").grid(row=2, column=2, sticky="w", padx=5, pady=4)
        self.expected_output_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.expected_output_var, width=26).grid(
            row=2, column=3, sticky="ew", padx=5, pady=4
        )

        # AsFoundOutput / AsLeftOutput
        ttk.Label(panel, text="As-Found Output:").grid(row=3, column=0, sticky="w", padx=5, pady=4)
        self.as_found_output_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.as_found_output_var, width=20).grid(
            row=3, column=1, sticky="ew", padx=5, pady=4
        )

        ttk.Label(panel, text="As-Left Output:").grid(row=3, column=2, sticky="w", padx=5, pady=4)
        self.as_left_output_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.as_left_output_var, width=26).grid(
            row=3, column=3, sticky="ew", padx=5, pady=4
        )

        # AsFoundError / AsFoundError_Percent
        ttk.Label(panel, text="As-Found Error:").grid(row=4, column=0, sticky="w", padx=5, pady=4)
        self.as_found_error_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.as_found_error_var, width=20).grid(
            row=4, column=1, sticky="ew", padx=5, pady=4
        )

        ttk.Label(panel, text="As-Found Error (%):").grid(row=4, column=2, sticky="w", padx=5, pady=4)
        self.as_found_error_percent_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.as_found_error_percent_var, width=26).grid(
            row=4, column=3, sticky="ew", padx=5, pady=4
        )

        # AsLeftError / AsLeftError_Percent
        ttk.Label(panel, text="As-Left Error:").grid(row=5, column=0, sticky="w", padx=5, pady=4)
        self.as_left_error_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.as_left_error_var, width=20).grid(
            row=5, column=1, sticky="ew", padx=5, pady=4
        )

        ttk.Label(panel, text="As-Left Error (%):").grid(row=5, column=2, sticky="w", padx=5, pady=4)
        self.as_left_error_percent_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.as_left_error_percent_var, width=26).grid(
            row=5, column=3, sticky="ew", padx=5, pady=4
        )

        ttk.Label(panel, text="* Required fields", foreground="gray").grid(
            row=6, column=0, columnspan=2, sticky="w", padx=5, pady=4
        )

        # Action buttons
        action_frame = ttk.Frame(panel)
        action_frame.grid(row=7, column=0, columnspan=4, sticky="e", padx=5, pady=(10, 5))
        ttk.Button(action_frame, text="New", command=self._new_record).pack(side="left", padx=3)
        ttk.Button(action_frame, text="Save", command=self._save_record).pack(side="left", padx=3)
        ttk.Button(action_frame, text="Delete", command=self._delete_record).pack(side="left", padx=3)
        ttk.Button(action_frame, text="Refresh", command=self.refresh_data).pack(side="left", padx=3)
        ttk.Button(
            action_frame, text="Reload Calibrations", command=self._load_calibration_lookup
        ).pack(side="left", padx=3)

    def _clear_filter(self):
        self.calibration_filter_var.set(
            "(All)" if "(All)" in self.calibration_filter_combo["values"] else ""
        )
        self.tolerance_filter_combo.set("(All)")
        self.refresh_data()

    # ------------------------------------------------------------------
    # Calibration Record FK lookup
    # ------------------------------------------------------------------
    def _load_calibration_lookup(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT cr.CalibrationID, i.TagNumber, cr.ActualDate, cr.CalibrationResult
                FROM CalibrationRecords cr
                LEFT JOIN Instruments i ON cr.InstrumentID = i.InstrumentID
                ORDER BY cr.ActualDate DESC
                """
            )
            rows = cursor.fetchall()
            conn.close()

            self.calibration_lookup = {}
            display_values = []
            for calibration_id, tag_number, actual_date, result in rows:
                date_str = actual_date.strftime("%Y-%m-%d") if actual_date else "No Date"
                display = f"{tag_number or 'Unknown'} - {date_str} (Cal #{calibration_id})"
                if result:
                    display += f" - {result}"
                self.calibration_lookup[display] = calibration_id
                display_values.append(display)

            self.calibration_combo["values"] = display_values
            self.calibration_filter_combo["values"] = ["(All)"] + display_values
            if not self.calibration_filter_var.get():
                self.calibration_filter_var.set("(All)")

        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to load Calibration Records lookup:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error while loading Calibration Records:\n{e}")

    def _calibration_display_for_id(self, calibration_id):
        for display, cid in self.calibration_lookup.items():
            if cid == calibration_id:
                return display
        return f"[ID {calibration_id}]"

    # ------------------------------------------------------------------
    # Data loading / search
    # ------------------------------------------------------------------
    def refresh_data(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()

            query = """
                SELECT ctp.TestPointID, ctp.CalibrationID, i.TagNumber, cr.ActualDate,
                       ctp.TestSequence, ctp.AppliedInput, ctp.AsFoundOutput,
                       ctp.AsLeftOutput, ctp.ExpectedOutput, ctp.IsWithinTolerance
                FROM CalibrationTestPoints ctp
                LEFT JOIN CalibrationRecords cr ON ctp.CalibrationID = cr.CalibrationID
                LEFT JOIN Instruments i ON cr.InstrumentID = i.InstrumentID
                WHERE 1=1
            """
            params = []

            calibration_display = self.calibration_filter_var.get()
            if calibration_display and calibration_display != "(All)":
                calibration_id = self.calibration_lookup.get(calibration_display)
                if calibration_id is not None:
                    query += " AND ctp.CalibrationID = ?"
                    params.append(calibration_id)

            tolerance_filter = self.tolerance_filter_var.get()
            if tolerance_filter and tolerance_filter != "(All)":
                query += " AND ctp.IsWithinTolerance = ?"
                params.append(1 if tolerance_filter == "Yes" else 0)

            query += " ORDER BY ctp.CalibrationID DESC, ctp.TestSequence"

            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()

            for item in self.tree.get_children():
                self.tree.delete(item)

            for row in rows:
                (test_point_id, calibration_id, tag_number, actual_date, test_sequence,
                 applied_input, as_found_output, as_left_output, expected_output,
                 is_within_tolerance) = row
                date_str = actual_date.strftime("%Y-%m-%d") if actual_date else ""
                calibration_label = f"{tag_number or 'Unknown'} - {date_str} (Cal #{calibration_id})"

                if is_within_tolerance is None:
                    tolerance_label = ""
                else:
                    tolerance_label = "Yes" if is_within_tolerance else "No"

                self.tree.insert(
                    "", "end", iid=str(test_point_id),
                    values=(
                        test_point_id, calibration_label,
                        test_sequence if test_sequence is not None else "",
                        applied_input if applied_input is not None else "",
                        as_found_output if as_found_output is not None else "",
                        as_left_output if as_left_output is not None else "",
                        expected_output if expected_output is not None else "",
                        tolerance_label,
                    )
                )

        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to load Calibration Test Points data:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error while loading data:\n{e}")

    # ------------------------------------------------------------------
    # Selection / form population
    # ------------------------------------------------------------------
    def _on_select(self, event):
        selection = self.tree.selection()
        if not selection:
            return

        test_point_id = int(selection[0])
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT TestPointID, CalibrationID, TestSequence, AppliedInput,
                       AsFoundOutput, AsLeftOutput, ExpectedOutput, AsFoundError,
                       AsFoundError_Percent, AsLeftError, AsLeftError_Percent,
                       IsWithinTolerance
                FROM CalibrationTestPoints
                WHERE TestPointID = ?
                """,
                (test_point_id,)
            )
            row = cursor.fetchone()
            conn.close()

            if not row:
                return

            (tpid, calibration_id, test_sequence, applied_input, as_found_output,
             as_left_output, expected_output, as_found_error, as_found_error_percent,
             as_left_error, as_left_error_percent, is_within_tolerance) = row

            self.selected_id = tpid
            self.id_var.set(str(tpid))
            self.calibration_var.set(self._calibration_display_for_id(calibration_id))
            self.test_sequence_var.set(str(test_sequence) if test_sequence is not None else "")
            self.applied_input_var.set(str(applied_input) if applied_input is not None else "")
            self.as_found_output_var.set(str(as_found_output) if as_found_output is not None else "")
            self.as_left_output_var.set(str(as_left_output) if as_left_output is not None else "")
            self.expected_output_var.set(str(expected_output) if expected_output is not None else "")
            self.as_found_error_var.set(str(as_found_error) if as_found_error is not None else "")
            self.as_found_error_percent_var.set(
                str(as_found_error_percent) if as_found_error_percent is not None else ""
            )
            self.as_left_error_var.set(str(as_left_error) if as_left_error is not None else "")
            self.as_left_error_percent_var.set(
                str(as_left_error_percent) if as_left_error_percent is not None else ""
            )

            if is_within_tolerance is None:
                self.within_tolerance_var.set("(Not Set)")
            else:
                self.within_tolerance_var.set("Yes" if is_within_tolerance else "No")

        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to load Test Point record:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error while loading record:\n{e}")

    def _new_record(self):
        self.selected_id = None
        self.id_var.set("")
        self.calibration_var.set("")
        self.test_sequence_var.set("")
        self.applied_input_var.set("")
        self.as_found_output_var.set("")
        self.as_left_output_var.set("")
        self.expected_output_var.set("")
        self.as_found_error_var.set("")
        self.as_found_error_percent_var.set("")
        self.as_left_error_var.set("")
        self.as_left_error_percent_var.set("")
        self.within_tolerance_var.set("(Not Set)")
        self.tree.selection_remove(self.tree.selection())

    # ------------------------------------------------------------------
    # Save (Insert / Update)
    # ------------------------------------------------------------------
    def _parse_decimal(self, var, label):
        raw = var.get().strip()
        if not raw:
            return None, True
        try:
            return float(raw), True
        except ValueError:
            messagebox.showwarning("Validation", f"{label} must be a number.")
            return None, False

    def _parse_int(self, var, label):
        raw = var.get().strip()
        if not raw:
            return None, True
        try:
            return int(raw), True
        except ValueError:
            messagebox.showwarning("Validation", f"{label} must be a whole number.")
            return None, False

    def _save_record(self):
        calibration_display = self.calibration_var.get().strip()
        if not calibration_display:
            messagebox.showwarning("Validation", "Please select a Calibration Record.")
            return

        calibration_id = self.calibration_lookup.get(calibration_display)
        if calibration_id is None:
            messagebox.showwarning("Validation", "Please select a valid Calibration Record from the list.")
            return

        test_sequence, ok = self._parse_int(self.test_sequence_var, "Test Sequence")
        if not ok:
            return
        applied_input, ok = self._parse_decimal(self.applied_input_var, "Applied Input")
        if not ok:
            return
        as_found_output, ok = self._parse_decimal(self.as_found_output_var, "As-Found Output")
        if not ok:
            return
        as_left_output, ok = self._parse_decimal(self.as_left_output_var, "As-Left Output")
        if not ok:
            return
        expected_output, ok = self._parse_decimal(self.expected_output_var, "Expected Output")
        if not ok:
            return
        as_found_error, ok = self._parse_decimal(self.as_found_error_var, "As-Found Error")
        if not ok:
            return
        as_found_error_percent, ok = self._parse_decimal(
            self.as_found_error_percent_var, "As-Found Error (%)"
        )
        if not ok:
            return
        as_left_error, ok = self._parse_decimal(self.as_left_error_var, "As-Left Error")
        if not ok:
            return
        as_left_error_percent, ok = self._parse_decimal(
            self.as_left_error_percent_var, "As-Left Error (%)"
        )
        if not ok:
            return

        tristate = self.within_tolerance_var.get()
        is_within_tolerance = None if tristate == "(Not Set)" else (1 if tristate == "Yes" else 0)

        try:
            conn = get_connection()
            cursor = conn.cursor()

            if self.selected_id:
                cursor.execute(
                    """
                    UPDATE CalibrationTestPoints
                    SET CalibrationID = ?, TestSequence = ?, AppliedInput = ?, AsFoundOutput = ?,
                        AsLeftOutput = ?, ExpectedOutput = ?, AsFoundError = ?,
                        AsFoundError_Percent = ?, AsLeftError = ?, AsLeftError_Percent = ?,
                        IsWithinTolerance = ?
                    WHERE TestPointID = ?
                    """,
                    (calibration_id, test_sequence, applied_input, as_found_output, as_left_output,
                     expected_output, as_found_error, as_found_error_percent, as_left_error,
                     as_left_error_percent, is_within_tolerance, self.selected_id)
                )
                conn.commit()
                messagebox.showinfo("Success", "Test Point updated successfully.")
            else:
                cursor.execute(
                    """
                    INSERT INTO CalibrationTestPoints
                    (CalibrationID, TestSequence, AppliedInput, AsFoundOutput, AsLeftOutput,
                     ExpectedOutput, AsFoundError, AsFoundError_Percent, AsLeftError,
                     AsLeftError_Percent, IsWithinTolerance)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (calibration_id, test_sequence, applied_input, as_found_output, as_left_output,
                     expected_output, as_found_error, as_found_error_percent, as_left_error,
                     as_left_error_percent, is_within_tolerance)
                )
                conn.commit()
                messagebox.showinfo("Success", "Test Point added successfully.")

            conn.close()
            self.refresh_data()
            self._new_record()

        except pyodbc.IntegrityError as e:
            messagebox.showerror(
                "Integrity Error",
                f"Save failed. This likely indicates an invalid Calibration Record reference:\n{e}"
            )
        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to save Test Point:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error while saving:\n{e}")

    # ------------------------------------------------------------------
    # Delete (with dynamic FK dependency check)
    # ------------------------------------------------------------------
    def _get_dependent_records(self, conn, test_point_id):
        """
        Dynamically discover every table with a FK referencing CalibrationTestPoints,
        then count rows that reference this TestPointID. Nothing references it
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
                    (test_point_id,)
                )
                count = count_cursor.fetchone()[0]
                if count > 0:
                    dependents.append((child_table, count))
            except pyodbc.Error:
                continue

        return dependents

    def _delete_record(self):
        if not self.selected_id:
            messagebox.showwarning("No Selection", "Please select a Test Point to delete.")
            return

        try:
            conn = get_connection()
            dependents = self._get_dependent_records(conn, self.selected_id)

            if dependents:
                detail = "\n".join(f"  - {table}: {count} record(s)" for table, count in dependents)
                proceed = messagebox.askyesno(
                    "Test Point In Use",
                    f"This Test Point is referenced by other records:\n\n{detail}\n\n"
                    "Deleting it may fail or orphan related data depending on your "
                    "database's FK constraints.\n\nDo you still want to attempt deletion?"
                )
                if not proceed:
                    conn.close()
                    return
            else:
                confirm = messagebox.askyesno(
                    "Confirm Delete",
                    f"Delete this Test Point (ID {self.selected_id})?"
                )
                if not confirm:
                    conn.close()
                    return

            cursor = conn.cursor()
            cursor.execute("DELETE FROM CalibrationTestPoints WHERE TestPointID = ?", (self.selected_id,))
            conn.commit()
            conn.close()

            messagebox.showinfo("Deleted", "Test Point deleted successfully.")
            self.refresh_data()
            self._new_record()

        except pyodbc.IntegrityError as e:
            messagebox.showerror(
                "Integrity Error",
                f"Cannot delete this Test Point because other records depend on it:\n{e}"
            )
        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to delete Test Point:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error while deleting:\n{e}")
