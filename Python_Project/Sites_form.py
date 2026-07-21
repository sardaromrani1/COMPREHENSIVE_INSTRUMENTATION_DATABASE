"""
Sites_form.py
CRUD form for the Sites table (top-level Site/Plant master data).

Pattern:
- ttk.Treeview list with column-scoped search (keyword for text columns,
  From/To DateEntry pickers for date columns)
- Detail/edit panel below/beside the list
- Save / New / Delete / Refresh buttons
- Identity PK (SiteID) rendered as a disabled entry
- Nullable date (CommissionDate) uses a "Set" checkbox pattern
- Delete checks for dependent child records dynamically via sys.foreign_keys
  before allowing deletion (Sites is referenced by ProcessUnits, ControlSystems,
  Instruments, etc. as the schema grows)
"""

import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import pyodbc
from datetime import datetime

from db_connection import get_connection


class SitesForm(ttk.Frame):

    TABLE_NAME = "Sites"
    PK_COLUMN = "SiteID"

    SITE_TYPES = ["Refinery", "Petrochemical", "Gas Plant", "Power Plant", "Other"]

    def __init__(self, parent):
        super().__init__(parent)
        self.selected_id = None

        self._build_ui()
        self.refresh_data()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------
    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        title = ttk.Label(self, text="Sites", font=("Segoe UI", 14, "bold"))
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

        # Keyword search (Site Code / Name / Location / Country / Capacity)
        ttk.Label(bar, text="Keyword:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.keyword_var = tk.StringVar()
        ttk.Entry(bar, textvariable=self.keyword_var).grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        # Site Type filter
        ttk.Label(bar, text="Site Type:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.type_filter_var = tk.StringVar()
        type_combo = ttk.Combobox(
            bar, textvariable=self.type_filter_var,
            values=["(All)"] + self.SITE_TYPES, state="readonly", width=15
        )
        type_combo.current(0)
        type_combo.grid(row=0, column=3, sticky="ew", padx=5, pady=5)

        # Active/Inactive filter
        ttk.Label(bar, text="Status:").grid(row=0, column=4, sticky="w", padx=5, pady=5)
        self.status_filter_var = tk.StringVar()
        status_combo = ttk.Combobox(
            bar, textvariable=self.status_filter_var,
            values=["(All)", "Active", "Inactive"], state="readonly", width=10
        )
        status_combo.current(0)
        status_combo.grid(row=0, column=5, sticky="ew", padx=5, pady=5)

        # Commission Date From/To
        ttk.Label(bar, text="Commission Date From:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.date_from = DateEntry(bar, date_pattern="yyyy-mm-dd", width=12)
        self.date_from.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        self.date_from_enabled = tk.BooleanVar(value=False)
        ttk.Checkbutton(bar, text="Use", variable=self.date_from_enabled).grid(row=1, column=1, sticky="e")

        ttk.Label(bar, text="To:").grid(row=1, column=2, sticky="e", padx=5, pady=5)
        self.date_to = DateEntry(bar, date_pattern="yyyy-mm-dd", width=12)
        self.date_to.grid(row=1, column=3, sticky="w", padx=5, pady=5)
        self.date_to_enabled = tk.BooleanVar(value=False)
        ttk.Checkbutton(bar, text="Use", variable=self.date_to_enabled).grid(row=1, column=3, sticky="e")

        btn_frame = ttk.Frame(bar)
        btn_frame.grid(row=1, column=5, columnspan=2, sticky="e", padx=5, pady=5)
        ttk.Button(btn_frame, text="Search", command=self.refresh_data).pack(side="left", padx=3)
        ttk.Button(btn_frame, text="Clear", command=self._clear_search).pack(side="left", padx=3)

    def _clear_search(self):
        self.keyword_var.set("")
        self.type_filter_var.set("(All)")
        self.status_filter_var.set("(All)")
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
            "SiteID", "SiteCode", "SiteName", "SiteType", "Location",
            "Country", "GPS_Latitude", "GPS_Longitude", "Capacity",
            "CommissionDate", "IsActive"
        )
        self.tree = ttk.Treeview(frame, columns=columns, show="headings", height=12)

        headings = {
            "SiteID": "ID", "SiteCode": "Site Code", "SiteName": "Site Name",
            "SiteType": "Type", "Location": "Location", "Country": "Country",
            "GPS_Latitude": "Latitude", "GPS_Longitude": "Longitude",
            "Capacity": "Capacity", "CommissionDate": "Commission Date",
            "IsActive": "Active"
        }
        widths = {
            "SiteID": 50, "SiteCode": 90, "SiteName": 160, "SiteType": 100,
            "Location": 150, "Country": 90, "GPS_Latitude": 90,
            "GPS_Longitude": 90, "Capacity": 110, "CommissionDate": 110,
            "IsActive": 60
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
        panel = ttk.LabelFrame(self, text="Site Details")
        panel.grid(row=3, column=0, sticky="ew", padx=10, pady=(5, 10))
        for c in range(4):
            panel.columnconfigure(c, weight=1)

        # SiteID (disabled, identity)
        ttk.Label(panel, text="Site ID:").grid(row=0, column=0, sticky="w", padx=5, pady=4)
        self.id_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.id_var, state="disabled", width=10).grid(
            row=0, column=1, sticky="w", padx=5, pady=4
        )

        # SiteCode (required)
        ttk.Label(panel, text="Site Code *:").grid(row=0, column=2, sticky="w", padx=5, pady=4)
        self.code_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.code_var, width=20).grid(
            row=0, column=3, sticky="ew", padx=5, pady=4
        )

        # SiteName (required)
        ttk.Label(panel, text="Site Name *:").grid(row=1, column=0, sticky="w", padx=5, pady=4)
        self.name_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.name_var, width=30).grid(
            row=1, column=1, columnspan=3, sticky="ew", padx=5, pady=4
        )

        # SiteType
        ttk.Label(panel, text="Site Type:").grid(row=2, column=0, sticky="w", padx=5, pady=4)
        self.type_var = tk.StringVar()
        ttk.Combobox(panel, textvariable=self.type_var, values=self.SITE_TYPES, width=18).grid(
            row=2, column=1, sticky="ew", padx=5, pady=4
        )

        # Country
        ttk.Label(panel, text="Country:").grid(row=2, column=2, sticky="w", padx=5, pady=4)
        self.country_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.country_var, width=20).grid(
            row=2, column=3, sticky="ew", padx=5, pady=4
        )

        # Location
        ttk.Label(panel, text="Location:").grid(row=3, column=0, sticky="w", padx=5, pady=4)
        self.location_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.location_var, width=30).grid(
            row=3, column=1, columnspan=3, sticky="ew", padx=5, pady=4
        )

        # GPS Latitude / Longitude
        ttk.Label(panel, text="GPS Latitude:").grid(row=4, column=0, sticky="w", padx=5, pady=4)
        self.lat_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.lat_var, width=20).grid(
            row=4, column=1, sticky="ew", padx=5, pady=4
        )

        ttk.Label(panel, text="GPS Longitude:").grid(row=4, column=2, sticky="w", padx=5, pady=4)
        self.lon_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.lon_var, width=20).grid(
            row=4, column=3, sticky="ew", padx=5, pady=4
        )

        # Capacity
        ttk.Label(panel, text="Capacity:").grid(row=5, column=0, sticky="w", padx=5, pady=4)
        self.capacity_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.capacity_var, width=20).grid(
            row=5, column=1, sticky="ew", padx=5, pady=4
        )

        # CommissionDate (nullable -> "Set" checkbox + DateEntry)
        ttk.Label(panel, text="Commission Date:").grid(row=5, column=2, sticky="w", padx=5, pady=4)
        date_frame = ttk.Frame(panel)
        date_frame.grid(row=5, column=3, sticky="w", padx=5, pady=4)
        self.commission_set_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            date_frame, text="Set", variable=self.commission_set_var,
            command=self._toggle_commission_date
        ).pack(side="left")
        self.commission_date = DateEntry(date_frame, date_pattern="yyyy-mm-dd", width=12, state="disabled")
        self.commission_date.pack(side="left", padx=5)

        # IsActive
        self.active_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(panel, text="Active", variable=self.active_var).grid(
            row=6, column=0, sticky="w", padx=5, pady=4
        )

        ttk.Label(panel, text="* Required fields", foreground="gray").grid(
            row=6, column=1, columnspan=2, sticky="w", padx=5, pady=4
        )

        # Action buttons
        action_frame = ttk.Frame(panel)
        action_frame.grid(row=7, column=0, columnspan=4, sticky="e", padx=5, pady=(10, 5))
        ttk.Button(action_frame, text="New", command=self._new_record).pack(side="left", padx=3)
        ttk.Button(action_frame, text="Save", command=self._save_record).pack(side="left", padx=3)
        ttk.Button(action_frame, text="Delete", command=self._delete_record).pack(side="left", padx=3)
        ttk.Button(action_frame, text="Refresh", command=self.refresh_data).pack(side="left", padx=3)

    def _toggle_commission_date(self):
        self.commission_date.configure(state="normal" if self.commission_set_var.get() else "disabled")

    # ------------------------------------------------------------------
    # Data loading / search
    # ------------------------------------------------------------------
    def refresh_data(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()

            query = """
                SELECT SiteID, SiteCode, SiteName, SiteType, Location, Country,
                       GPS_Latitude, GPS_Longitude, Capacity, CommissionDate, IsActive
                FROM Sites
                WHERE 1 = 1
            """
            params = []

            keyword = self.keyword_var.get().strip()
            if keyword:
                query += """ AND (
                    SiteCode LIKE ? OR SiteName LIKE ? OR Location LIKE ?
                    OR Country LIKE ? OR Capacity LIKE ?
                )"""
                like = f"%{keyword}%"
                params.extend([like, like, like, like, like])

            site_type = self.type_filter_var.get()
            if site_type and site_type != "(All)":
                query += " AND SiteType = ?"
                params.append(site_type)

            status = self.status_filter_var.get()
            if status == "Active":
                query += " AND IsActive = 1"
            elif status == "Inactive":
                query += " AND IsActive = 0"

            if self.date_from_enabled.get():
                query += " AND CommissionDate >= ?"
                params.append(self.date_from.get_date())

            if self.date_to_enabled.get():
                query += " AND CommissionDate <= ?"
                params.append(self.date_to.get_date())

            query += " ORDER BY SiteName"

            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()

            self.tree.delete(*self.tree.get_children())
            for row in rows:
                values = list(row)
                # Format date and boolean nicely
                if values[9] is not None:
                    values[9] = values[9].strftime("%Y-%m-%d")
                values[10] = "Yes" if values[10] else "No"
                self.tree.insert("", "end", values=values)

        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to load Sites data:\n{e}")
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

        self.id_var.set(values[0])
        self.code_var.set(values[1])
        self.name_var.set(values[2])
        self.type_var.set(values[3] or "")
        self.location_var.set(values[4] or "")
        self.country_var.set(values[5] or "")
        self.lat_var.set(values[6] if values[6] is not None else "")
        self.lon_var.set(values[7] if values[7] is not None else "")
        self.capacity_var.set(values[8] or "")

        if values[9]:
            self.commission_set_var.set(True)
            self.commission_date.configure(state="normal")
            self.commission_date.set_date(datetime.strptime(values[9], "%Y-%m-%d"))
        else:
            self.commission_set_var.set(False)
            self.commission_date.configure(state="disabled")

        self.active_var.set(values[10] == "Yes")

    def _new_record(self):
        self.selected_id = None
        self.tree.selection_remove(self.tree.selection())

        self.id_var.set("")
        self.code_var.set("")
        self.name_var.set("")
        self.type_var.set("")
        self.location_var.set("")
        self.country_var.set("")
        self.lat_var.set("")
        self.lon_var.set("")
        self.capacity_var.set("")
        self.commission_set_var.set(False)
        self.commission_date.configure(state="disabled")
        self.active_var.set(True)

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    def _validate_form(self):
        if not self.code_var.get().strip():
            messagebox.showwarning("Validation", "Site Code is required.")
            return False
        if not self.name_var.get().strip():
            messagebox.showwarning("Validation", "Site Name is required.")
            return False

        lat_str = self.lat_var.get().strip()
        if lat_str:
            try:
                lat = float(lat_str)
                if not (-90 <= lat <= 90):
                    messagebox.showwarning("Validation", "GPS Latitude must be between -90 and 90.")
                    return False
            except ValueError:
                messagebox.showwarning("Validation", "GPS Latitude must be a valid number.")
                return False

        lon_str = self.lon_var.get().strip()
        if lon_str:
            try:
                lon = float(lon_str)
                if not (-180 <= lon <= 180):
                    messagebox.showwarning("Validation", "GPS Longitude must be between -180 and 180.")
                    return False
            except ValueError:
                messagebox.showwarning("Validation", "GPS Longitude must be a valid number.")
                return False

        return True

    # ------------------------------------------------------------------
    # Save (Insert / Update)
    # ------------------------------------------------------------------
    def _save_record(self):
        if not self._validate_form():
            return

        site_code = self.code_var.get().strip()
        site_name = self.name_var.get().strip()
        site_type = self.type_var.get().strip() or None
        location = self.location_var.get().strip() or None
        country = self.country_var.get().strip() or None
        lat = float(self.lat_var.get()) if self.lat_var.get().strip() else None
        lon = float(self.lon_var.get()) if self.lon_var.get().strip() else None
        capacity = self.capacity_var.get().strip() or None
        commission_date = self.commission_date.get_date() if self.commission_set_var.get() else None
        is_active = 1 if self.active_var.get() else 0

        try:
            conn = get_connection()
            cursor = conn.cursor()

            if self.selected_id:
                cursor.execute(
                    """
                    UPDATE Sites
                    SET SiteCode = ?, SiteName = ?, SiteType = ?, Location = ?,
                        Country = ?, GPS_Latitude = ?, GPS_Longitude = ?,
                        Capacity = ?, CommissionDate = ?, IsActive = ?
                    WHERE SiteID = ?
                    """,
                    (site_code, site_name, site_type, location, country,
                     lat, lon, capacity, commission_date, is_active, self.selected_id)
                )
                conn.commit()
                messagebox.showinfo("Success", "Site updated successfully.")
            else:
                cursor.execute(
                    """
                    INSERT INTO Sites
                        (SiteCode, SiteName, SiteType, Location, Country,
                         GPS_Latitude, GPS_Longitude, Capacity, CommissionDate, IsActive)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (site_code, site_name, site_type, location, country,
                     lat, lon, capacity, commission_date, is_active)
                )
                conn.commit()
                messagebox.showinfo("Success", "Site added successfully.")

            conn.close()
            self.refresh_data()
            self._new_record()

        except pyodbc.IntegrityError as e:
            messagebox.showerror(
                "Integrity Error",
                f"Save failed. This likely violates a unique constraint "
                f"(Site Code must be unique):\n{e}"
            )
        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to save Site:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error while saving:\n{e}")

    # ------------------------------------------------------------------
    # Delete (with dynamic FK dependency check)
    # ------------------------------------------------------------------
    def _get_dependent_records(self, conn, site_id):
        """
        Dynamically discover every table with a FK referencing Sites,
        then count rows that reference this SiteID. This avoids hardcoding
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
                    (site_id,)
                )
                count = count_cursor.fetchone()[0]
                if count > 0:
                    dependents.append((child_table, count))
            except pyodbc.Error:
                # If a particular child table can't be queried, skip it rather
                # than block the whole dependency check.
                continue

        return dependents

    def _delete_record(self):
        if not self.selected_id:
            messagebox.showwarning("No Selection", "Please select a Site to delete.")
            return

        try:
            conn = get_connection()
            dependents = self._get_dependent_records(conn, self.selected_id)

            if dependents:
                detail = "\n".join(f"  - {table}: {count} record(s)" for table, count in dependents)
                proceed = messagebox.askyesno(
                    "Site In Use",
                    f"This Site is referenced by other records:\n\n{detail}\n\n"
                    "Deleting it may fail or orphan related data depending on your "
                    "database's FK constraints.\n\nDo you still want to attempt deletion?"
                )
                if not proceed:
                    conn.close()
                    return
            else:
                confirm = messagebox.askyesno(
                    "Confirm Delete",
                    f"Delete Site '{self.name_var.get()}' (ID {self.selected_id})?"
                )
                if not confirm:
                    conn.close()
                    return

            cursor = conn.cursor()
            cursor.execute("DELETE FROM Sites WHERE SiteID = ?", (self.selected_id,))
            conn.commit()
            conn.close()

            messagebox.showinfo("Deleted", "Site deleted successfully.")
            self.refresh_data()
            self._new_record()

        except pyodbc.IntegrityError as e:
            messagebox.showerror(
                "Integrity Error",
                f"Cannot delete this Site because other records depend on it:\n{e}"
            )
        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to delete Site:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error while deleting:\n{e}")
