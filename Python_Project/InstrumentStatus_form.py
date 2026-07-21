"""
InstrumentStatus_form.py

CRUD form for the InstrumentStatus lookup table.

    CREATE TABLE InstrumentStatus(
        StatusCode VARCHAR(30) PRIMARY KEY,
        Description NVARCHAR(100)
    );

Follows the same conventions as the other forms in this project:
    - get_connection() from db_connection (pyodbc / ODBC Driver 17 / Windows Auth)
    - String PK (StatusCode) locked (disabled) after a record is selected,
      since it can't be changed once it may be referenced elsewhere
    - pyodbc.IntegrityError caught separately for meaningful constraint messages
    - Dynamic FK-dependency check on delete using sys.foreign_keys
    - Column-scoped search / filter panel with live keyword filtering
"""

import tkinter as tk
from tkinter import ttk, messagebox

import pyodbc

from db_connection import get_connection


class InstrumentStatusForm(ttk.Frame):
    TABLE_NAME = "InstrumentStatus"

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.selected_code = None
        self.is_new_record = True

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
            values=["(All Columns)", "StatusCode", "Description"]
        )
        self.search_column_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=4)

        ttk.Label(filter_frame, text="Keyword:").grid(row=0, column=2, sticky="w", padx=5, pady=4)
        self.search_text_var = tk.StringVar()
        search_entry = ttk.Entry(filter_frame, textvariable=self.search_text_var, width=28)
        search_entry.grid(row=0, column=3, sticky="ew", padx=5, pady=4)
        search_entry.bind("<KeyRelease>", lambda e: self.refresh_data())

        btn_frame = ttk.Frame(filter_frame)
        btn_frame.grid(row=1, column=0, columnspan=4, sticky="w", padx=5, pady=(0, 4))
        ttk.Button(btn_frame, text="Apply Filter", command=self.refresh_data).pack(side="left", padx=3)
        ttk.Button(btn_frame, text="Clear Filter", command=self._clear_filter).pack(side="left", padx=3)

        for col in range(4):
            filter_frame.columnconfigure(col, weight=1)

        # ---------------- Treeview ----------------
        tree_frame = ttk.Frame(self)
        tree_frame.pack(side="top", fill="both", expand=True, padx=8, pady=4)

        columns = ("StatusCode", "Description")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=10)
        headings = {"StatusCode": "Status Code", "Description": "Description"}
        widths = {"StatusCode": 150, "Description": 350}
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
        panel = ttk.LabelFrame(self, text="Status Details")
        panel.pack(side="top", fill="x", padx=8, pady=4)
        for col in range(4):
            panel.columnconfigure(col, weight=1)

        # StatusCode (PK, required, locked after selection)
        ttk.Label(panel, text="Status Code *:").grid(row=0, column=0, sticky="w", padx=5, pady=4)
        self.code_var = tk.StringVar()
        self.code_entry = ttk.Entry(panel, textvariable=self.code_var, width=20)
        self.code_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=4)

        # Description
        ttk.Label(panel, text="Description:").grid(row=0, column=2, sticky="w", padx=5, pady=4)
        self.description_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.description_var, width=32).grid(
            row=0, column=3, sticky="ew", padx=5, pady=4
        )

        ttk.Label(panel, text="* Required fields", foreground="gray").grid(
            row=1, column=0, columnspan=2, sticky="w", padx=5, pady=4
        )
        ttk.Label(
            panel, text="Status Code cannot be changed once a record is selected.",
            foreground="gray"
        ).grid(row=1, column=2, columnspan=2, sticky="w", padx=5, pady=4)

        # Action buttons
        action_frame = ttk.Frame(panel)
        action_frame.grid(row=2, column=0, columnspan=4, sticky="e", padx=5, pady=(10, 5))
        ttk.Button(action_frame, text="New", command=self._new_record).pack(side="left", padx=3)
        ttk.Button(action_frame, text="Save", command=self._save_record).pack(side="left", padx=3)
        ttk.Button(action_frame, text="Delete", command=self._delete_record).pack(side="left", padx=3)
        ttk.Button(action_frame, text="Refresh", command=self.refresh_data).pack(side="left", padx=3)

    def _clear_filter(self):
        self.search_column_var.set("(All Columns)")
        self.search_text_var.set("")
        self.refresh_data()

    # ------------------------------------------------------------------
    # Data loading / search
    # ------------------------------------------------------------------
    def refresh_data(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()

            query = "SELECT StatusCode, Description FROM InstrumentStatus WHERE 1=1"
            params = []

            keyword = self.search_text_var.get().strip()
            if keyword:
                column = self.search_column_var.get()
                like_value = f"%{keyword}%"
                if column == "StatusCode":
                    query += " AND StatusCode LIKE ?"
                    params.append(like_value)
                elif column == "Description":
                    query += " AND Description LIKE ?"
                    params.append(like_value)
                else:
                    query += " AND (StatusCode LIKE ? OR Description LIKE ?)"
                    params.extend([like_value, like_value])

            query += " ORDER BY StatusCode"

            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()

            for item in self.tree.get_children():
                self.tree.delete(item)

            for status_code, description in rows:
                self.tree.insert(
                    "", "end", iid=status_code,
                    values=(status_code, description or "")
                )

        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to load Instrument Status data:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error while loading data:\n{e}")

    # ------------------------------------------------------------------
    # Selection / form population
    # ------------------------------------------------------------------
    def _on_select(self, event):
        selection = self.tree.selection()
        if not selection:
            return

        status_code = selection[0]
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT StatusCode, Description FROM InstrumentStatus WHERE StatusCode = ?",
                (status_code,)
            )
            row = cursor.fetchone()
            conn.close()

            if not row:
                return

            code, description = row

            self.selected_code = code
            self.is_new_record = False
            self.code_var.set(code)
            self.description_var.set(description or "")
            self.code_entry.configure(state="disabled")

        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to load Status record:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error while loading record:\n{e}")

    def _new_record(self):
        self.selected_code = None
        self.is_new_record = True
        self.code_var.set("")
        self.description_var.set("")
        self.code_entry.configure(state="normal")
        self.tree.selection_remove(self.tree.selection())

    # ------------------------------------------------------------------
    # Save (Insert / Update)
    # ------------------------------------------------------------------
    def _save_record(self):
        status_code = self.code_var.get().strip()
        description = self.description_var.get().strip() or None

        if not status_code:
            messagebox.showwarning("Validation", "Please enter a Status Code.")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()

            if self.is_new_record:
                cursor.execute(
                    """
                    INSERT INTO InstrumentStatus (StatusCode, Description)
                    VALUES (?, ?)
                    """,
                    (status_code, description)
                )
                conn.commit()
                messagebox.showinfo("Success", "Status added successfully.")
            else:
                cursor.execute(
                    """
                    UPDATE InstrumentStatus
                    SET Description = ?
                    WHERE StatusCode = ?
                    """,
                    (description, self.selected_code)
                )
                conn.commit()
                messagebox.showinfo("Success", "Status updated successfully.")

            conn.close()
            self.refresh_data()
            self._new_record()

        except pyodbc.IntegrityError as e:
            messagebox.showerror(
                "Integrity Error",
                f"Save failed. This likely violates a unique constraint "
                f"(Status Code must be unique):\n{e}"
            )
        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to save Status:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error while saving:\n{e}")

    # ------------------------------------------------------------------
    # Delete (with dynamic FK dependency check)
    # ------------------------------------------------------------------
    def _get_dependent_records(self, conn, status_code):
        """
        Dynamically discover every table with a FK referencing InstrumentStatus,
        then count rows that reference this StatusCode. This avoids hardcoding
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
                    (status_code,)
                )
                count = count_cursor.fetchone()[0]
                if count > 0:
                    dependents.append((child_table, count))
            except pyodbc.Error:
                continue

        return dependents

    def _delete_record(self):
        if not self.selected_code:
            messagebox.showwarning("No Selection", "Please select a Status to delete.")
            return

        try:
            conn = get_connection()
            dependents = self._get_dependent_records(conn, self.selected_code)

            if dependents:
                detail = "\n".join(f"  - {table}: {count} record(s)" for table, count in dependents)
                proceed = messagebox.askyesno(
                    "Status In Use",
                    f"This Status is referenced by other records:\n\n{detail}\n\n"
                    "Deleting it may fail or orphan related data depending on your "
                    "database's FK constraints.\n\nDo you still want to attempt deletion?"
                )
                if not proceed:
                    conn.close()
                    return
            else:
                confirm = messagebox.askyesno(
                    "Confirm Delete",
                    f"Delete Status '{self.selected_code}'?"
                )
                if not confirm:
                    conn.close()
                    return

            cursor = conn.cursor()
            cursor.execute("DELETE FROM InstrumentStatus WHERE StatusCode = ?", (self.selected_code,))
            conn.commit()
            conn.close()

            messagebox.showinfo("Deleted", "Status deleted successfully.")
            self.refresh_data()
            self._new_record()

        except pyodbc.IntegrityError as e:
            messagebox.showerror(
                "Integrity Error",
                f"Cannot delete this Status because other records depend on it:\n{e}"
            )
        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to delete Status:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error while deleting:\n{e}")
