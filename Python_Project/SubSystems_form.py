"""
SubSystems_form.py
CRUD form for the SubSystems table.

Pattern:
- ttk.Treeview list with column-scoped search (keyword + Unit/Site filter)
- Detail/edit panel with a required FK combobox for Unit (ProcessUnits)
- Save / New / Delete / Refresh buttons
- Identity PK (SubSystemID) rendered as a disabled entry
- Delete checks for dependent child records dynamically via sys.foreign_keys
  before allowing deletion (SubSystems is likely referenced by Instruments,
  ControlLoops, etc. as the schema grows)
"""

import tkinter as tk
from tkinter import ttk, messagebox
import pyodbc

from db_connection import get_connection


class SubSystemsForm(ttk.Frame):

    TABLE_NAME = "SubSystems"
    PK_COLUMN = "SubSystemID"

    def __init__(self, parent):
        super().__init__(parent)
        self.selected_id = None
        self.unit_lookup = {}  # display string -> UnitID

        self._build_ui()
        self._load_unit_lookup()
        self.refresh_data()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------
    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        title = ttk.Label(self, text="Sub-Systems", font=("Segoe UI", 14, "bold"))
        title.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 5))

        self._build_search_bar()
        self._build_treeview()
        self._build_detail_panel()

    # -- Search bar -----------------------------------------------------
    def _build_search_bar(self):
        bar = ttk.LabelFrame(self, text="Search")
        bar.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        for c in range(6):
            bar.columnconfigure(c, weight=1)

        ttk.Label(bar, text="Keyword:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.keyword_var = tk.StringVar()
        ttk.Entry(bar, textvariable=self.keyword_var).grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(bar, text="Process Unit:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.unit_filter_var = tk.StringVar()
        self.unit_filter_combo = ttk.Combobox(
            bar, textvariable=self.unit_filter_var, state="readonly", width=25
        )
        self.unit_filter_combo.grid(row=0, column=3, sticky="ew", padx=5, pady=5)

        btn_frame = ttk.Frame(bar)
        btn_frame.grid(row=0, column=4, columnspan=2, sticky="e", padx=5, pady=5)
        ttk.Button(btn_frame, text="Search", command=self.refresh_data).pack(side="left", padx=3)
        ttk.Button(btn_frame, text="Clear", command=self._clear_search).pack(side="left", padx=3)

    def _clear_search(self):
        self.keyword_var.set("")
        self.unit_filter_var.set("(All)")
        self.refresh_data()

    # -- Treeview ---------------------------------------------------------
    def _build_treeview(self):
        frame = ttk.Frame(self)
        frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        columns = (
            "SubSystemID", "SubSystemCode", "SubSystemName", "UnitName",
            "SiteName", "Description"
        )
        self.tree = ttk.Treeview(frame, columns=columns, show="headings", height=12)

        headings = {
            "SubSystemID": "ID", "SubSystemCode": "Sub-System Code",
            "SubSystemName": "Sub-System Name", "UnitName": "Process Unit",
            "SiteName": "Site", "Description": "Description"
        }
        widths = {
            "SubSystemID": 50, "SubSystemCode": 120, "SubSystemName": 170,
            "UnitName": 150, "SiteName": 120, "Description": 250
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
        panel = ttk.LabelFrame(self, text="Sub-System Details")
        panel.grid(row=3, column=0, sticky="ew", padx=10, pady=(5, 10))
        for c in range(4):
            panel.columnconfigure(c, weight=1)

        # SubSystemID (disabled, identity)
        ttk.Label(panel, text="Sub-System ID:").grid(row=0, column=0, sticky="w", padx=5, pady=4)
        self.id_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.id_var, state="disabled", width=10).grid(
            row=0, column=1, sticky="w", padx=5, pady=4
        )

        # Process Unit (FK combo, required)
        ttk.Label(panel, text="Process Unit *:").grid(row=0, column=2, sticky="w", padx=5, pady=4)
        self.unit_var = tk.StringVar()
        self.unit_combo = ttk.Combobox(panel, textvariable=self.unit_var, state="readonly", width=28)
        self.unit_combo.grid(row=0, column=3, sticky="ew", padx=5, pady=4)

        # SubSystemCode (required, unique)
        ttk.Label(panel, text="Sub-System Code *:").grid(row=1, column=0, sticky="w", padx=5, pady=4)
        self.code_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.code_var, width=20).grid(
            row=1, column=1, sticky="ew", padx=5, pady=4
        )

        # SubSystemName (required)
        ttk.Label(panel, text="Sub-System Name *:").grid(row=1, column=2, sticky="w", padx=5, pady=4)
        self.name_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.name_var, width=28).grid(
            row=1, column=3, sticky="ew", padx=5, pady=4
        )

        # Description (multi-line, 500 chars)
        ttk.Label(panel, text="Description:").grid(row=2, column=0, sticky="nw", padx=5, pady=4)
        desc_frame = ttk.Frame(panel)
        desc_frame.grid(row=2, column=1, columnspan=3, sticky="ew", padx=5, pady=4)
        self.description_text = tk.Text(desc_frame, height=4, width=50, wrap="word")
        desc_scroll = ttk.Scrollbar(desc_frame, orient="vertical", command=self.description_text.yview)
        self.description_text.configure(yscrollcommand=desc_scroll.set)
        self.description_text.pack(side="left", fill="both", expand=True)
        desc_scroll.pack(side="right", fill="y")

        ttk.Label(panel, text="* Required fields", foreground="gray").grid(
            row=3, column=0, columnspan=2, sticky="w", padx=5, pady=4
        )

        # Action buttons
        action_frame = ttk.Frame(panel)
        action_frame.grid(row=4, column=0, columnspan=4, sticky="e", padx=5, pady=(10, 5))
        ttk.Button(action_frame, text="New", command=self._new_record).pack(side="left", padx=3)
        ttk.Button(action_frame, text="Save", command=self._save_record).pack(side="left", padx=3)
        ttk.Button(action_frame, text="Delete", command=self._delete_record).pack(side="left", padx=3)
        ttk.Button(action_frame, text="Refresh", command=self.refresh_data).pack(side="left", padx=3)
        ttk.Button(action_frame, text="Reload Units", command=self._load_unit_lookup).pack(side="left", padx=3)

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

    # ------------------------------------------------------------------
    # Data loading / search
    # ------------------------------------------------------------------
    def refresh_data(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()

            query = """
                SELECT ss.SubSystemID, ss.SubSystemCode, ss.SubSystemName,
                       pu.UnitName, s.SiteName, ss.Description
                FROM SubSystems ss
                LEFT JOIN ProcessUnits pu ON ss.UnitID = pu.UnitID
                LEFT JOIN Sites s ON pu.SiteID = s.SiteID
                WHERE 1 = 1
            """
            params = []

            keyword = self.keyword_var.get().strip()
            if keyword:
                query += """ AND (
                    ss.SubSystemCode LIKE ? OR ss.SubSystemName LIKE ? OR ss.Description LIKE ?
                )"""
                like = f"%{keyword}%"
                params.extend([like, like, like])

            unit_display = self.unit_filter_var.get()
            if unit_display and unit_display != "(All)":
                unit_id = self.unit_lookup.get(unit_display)
                if unit_id is not None:
                    query += " AND ss.UnitID = ?"
                    params.append(unit_id)

            query += " ORDER BY ss.SubSystemName"

            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()

            self.tree.delete(*self.tree.get_children())
            for row in rows:
                self.tree.insert("", "end", values=list(row))

        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to load Sub-Systems data:\n{e}")
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
                SELECT UnitID, SubSystemCode, SubSystemName, Description
                FROM SubSystems WHERE SubSystemID = ?
                """,
                (self.selected_id,)
            )
            row = cursor.fetchone()
            conn.close()

            if row is None:
                return

            unit_id, code, name, description = row

            self.id_var.set(self.selected_id)

            unit_display = next(
                (disp for disp, uid in self.unit_lookup.items() if uid == unit_id), ""
            )
            self.unit_var.set(unit_display)

            self.code_var.set(code)
            self.name_var.set(name)

            self.description_text.delete("1.0", "end")
            if description:
                self.description_text.insert("1.0", description)

        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to load Sub-System details:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error while loading details:\n{e}")

    def _new_record(self):
        self.selected_id = None
        self.tree.selection_remove(self.tree.selection())

        self.id_var.set("")
        self.unit_var.set("")
        self.code_var.set("")
        self.name_var.set("")
        self.description_text.delete("1.0", "end")

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    def _validate_form(self):
        if not self.unit_var.get().strip():
            messagebox.showwarning("Validation", "Process Unit is required.")
            return False
        if not self.code_var.get().strip():
            messagebox.showwarning("Validation", "Sub-System Code is required.")
            return False
        if not self.name_var.get().strip():
            messagebox.showwarning("Validation", "Sub-System Name is required.")
            return False
        return True

    # ------------------------------------------------------------------
    # Save (Insert / Update)
    # ------------------------------------------------------------------
    def _save_record(self):
        if not self._validate_form():
            return

        unit_id = self.unit_lookup.get(self.unit_var.get())
        if unit_id is None:
            messagebox.showwarning("Validation", "Please select a valid Process Unit.")
            return

        code = self.code_var.get().strip()
        name = self.name_var.get().strip()
        description = self.description_text.get("1.0", "end").strip() or None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            if self.selected_id:
                cursor.execute(
                    """
                    UPDATE SubSystems
                    SET UnitID = ?, SubSystemCode = ?, SubSystemName = ?, Description = ?
                    WHERE SubSystemID = ?
                    """,
                    (unit_id, code, name, description, self.selected_id)
                )
                conn.commit()
                messagebox.showinfo("Success", "Sub-System updated successfully.")
            else:
                cursor.execute(
                    """
                    INSERT INTO SubSystems (UnitID, SubSystemCode, SubSystemName, Description)
                    VALUES (?, ?, ?, ?)
                    """,
                    (unit_id, code, name, description)
                )
                conn.commit()
                messagebox.showinfo("Success", "Sub-System added successfully.")

            conn.close()
            self.refresh_data()
            self._new_record()

        except pyodbc.IntegrityError as e:
            messagebox.showerror(
                "Integrity Error",
                f"Save failed. This likely violates a unique constraint "
                f"(Sub-System Code must be unique) or an invalid Process Unit reference:\n{e}"
            )
        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to save Sub-System:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error while saving:\n{e}")

    # ------------------------------------------------------------------
    # Delete (with dynamic FK dependency check)
    # ------------------------------------------------------------------
    def _get_dependent_records(self, conn, subsystem_id):
        """
        Dynamically discover every table with a FK referencing SubSystems,
        then count rows that reference this SubSystemID. This avoids
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
                    (subsystem_id,)
                )
                count = count_cursor.fetchone()[0]
                if count > 0:
                    dependents.append((child_table, count))
            except pyodbc.Error:
                continue

        return dependents

    def _delete_record(self):
        if not self.selected_id:
            messagebox.showwarning("No Selection", "Please select a Sub-System to delete.")
            return

        try:
            conn = get_connection()
            dependents = self._get_dependent_records(conn, self.selected_id)

            if dependents:
                detail = "\n".join(f"  - {table}: {count} record(s)" for table, count in dependents)
                proceed = messagebox.askyesno(
                    "Sub-System In Use",
                    f"This Sub-System is referenced by other records:\n\n{detail}\n\n"
                    "Deleting it may fail or orphan related data depending on your "
                    "database's FK constraints.\n\nDo you still want to attempt deletion?"
                )
                if not proceed:
                    conn.close()
                    return
            else:
                confirm = messagebox.askyesno(
                    "Confirm Delete",
                    f"Delete Sub-System '{self.name_var.get()}' (ID {self.selected_id})?"
                )
                if not confirm:
                    conn.close()
                    return

            cursor = conn.cursor()
            cursor.execute("DELETE FROM SubSystems WHERE SubSystemID = ?", (self.selected_id,))
            conn.commit()
            conn.close()

            messagebox.showinfo("Deleted", "Sub-System deleted successfully.")
            self.refresh_data()
            self._new_record()

        except pyodbc.IntegrityError as e:
            messagebox.showerror(
                "Integrity Error",
                f"Cannot delete this Sub-System because other records depend on it:\n{e}"
            )
        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to delete Sub-System:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error while deleting:\n{e}")
