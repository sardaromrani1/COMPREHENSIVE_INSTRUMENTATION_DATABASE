"""
Manufacturers_form.py
CRUD form for the Manufacturers table (vendor/manufacturer master data).

Pattern (consistent with Sites_form.py):
- ttk.Treeview list with column-scoped search (keyword + dropdown filters)
- Detail/edit panel below the list
- Save / New / Delete / Refresh buttons
- Identity PK (ManufacturerID) rendered as a disabled entry
- Rating fields (0.00-5.00) validated as decimals in range
- Notes uses a scrolled Text widget (NVARCHAR(1000), too long for an Entry)
- Delete checks for dependent child records dynamically via sys.foreign_keys
  before allowing deletion (Manufacturers is referenced by Instruments and
  potentially other tables as the schema grows)

Note: This table has no DATE columns, so no DateEntry pickers are needed here.
"""

import re
import tkinter as tk
from tkinter import ttk, messagebox
import pyodbc

from db_connection import get_connection


class ManufacturersForm(ttk.Frame):

    TABLE_NAME = "Manufacturers"
    PK_COLUMN = "ManufacturerID"

    EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

    def __init__(self, parent):
        super().__init__(parent)
        self.selected_id = None
        self._row_cache = {}

        self._build_ui()
        self.refresh_data()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------
    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        title = ttk.Label(self, text="Manufacturers", font=("Segoe UI", 14, "bold"))
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

        # Keyword search
        ttk.Label(bar, text="Keyword:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.keyword_var = tk.StringVar()
        ttk.Entry(bar, textvariable=self.keyword_var).grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        ttk.Label(bar, text="(Name / Short Name / Country / Contact / Rep)", foreground="gray").grid(
            row=0, column=2, columnspan=2, sticky="w", padx=5
        )

        # Approved Vendor filter
        ttk.Label(bar, text="Approved:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.approved_filter_var = tk.StringVar()
        approved_combo = ttk.Combobox(
            bar, textvariable=self.approved_filter_var,
            values=["(All)", "Yes", "No"], state="readonly", width=10
        )
        approved_combo.current(0)
        approved_combo.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        # Service Center filter
        ttk.Label(bar, text="Service Center:").grid(row=1, column=2, sticky="w", padx=5, pady=5)
        self.service_filter_var = tk.StringVar()
        service_combo = ttk.Combobox(
            bar, textvariable=self.service_filter_var,
            values=["(All)", "Yes", "No"], state="readonly", width=10
        )
        service_combo.current(0)
        service_combo.grid(row=1, column=3, sticky="w", padx=5, pady=5)

        # Min Quality Rating filter
        ttk.Label(bar, text="Min Quality Rating:").grid(row=1, column=4, sticky="w", padx=5, pady=5)
        self.min_rating_var = tk.StringVar()
        ttk.Entry(bar, textvariable=self.min_rating_var, width=8).grid(
            row=1, column=5, sticky="w", padx=5, pady=5
        )

        btn_frame = ttk.Frame(bar)
        btn_frame.grid(row=1, column=6, columnspan=2, sticky="e", padx=5, pady=5)
        ttk.Button(btn_frame, text="Search", command=self.refresh_data).pack(side="left", padx=3)
        ttk.Button(btn_frame, text="Clear", command=self._clear_search).pack(side="left", padx=3)

    def _clear_search(self):
        self.keyword_var.set("")
        self.approved_filter_var.set("(All)")
        self.service_filter_var.set("(All)")
        self.min_rating_var.set("")
        self.refresh_data()

    # -- Treeview ---------------------------------------------------------
    def _build_treeview(self):
        frame = ttk.Frame(self)
        frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        columns = (
            "ManufacturerID", "ManufacturerName", "ShortName", "Country",
            "ContactEmail", "ContactPhone", "LocalRepresentative",
            "IsApprovedVendor", "QualityRating", "DeliveryRating",
            "TechnicalSupportRating", "HasServiceCenter"
        )
        self.tree = ttk.Treeview(frame, columns=columns, show="headings", height=12)

        headings = {
            "ManufacturerID": "ID", "ManufacturerName": "Manufacturer Name",
            "ShortName": "Short Name", "Country": "Country",
            "ContactEmail": "Contact Email", "ContactPhone": "Contact Phone",
            "LocalRepresentative": "Local Rep", "IsApprovedVendor": "Approved",
            "QualityRating": "Quality", "DeliveryRating": "Delivery",
            "TechnicalSupportRating": "Tech Support", "HasServiceCenter": "Svc Center"
        }
        widths = {
            "ManufacturerID": 50, "ManufacturerName": 170, "ShortName": 100,
            "Country": 90, "ContactEmail": 150, "ContactPhone": 100,
            "LocalRepresentative": 130, "IsApprovedVendor": 70,
            "QualityRating": 60, "DeliveryRating": 60,
            "TechnicalSupportRating": 80, "HasServiceCenter": 70
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
        panel = ttk.LabelFrame(self, text="Manufacturer Details")
        panel.grid(row=3, column=0, sticky="ew", padx=10, pady=(5, 10))
        for c in range(4):
            panel.columnconfigure(c, weight=1)

        # ManufacturerID (disabled, identity)
        ttk.Label(panel, text="Manufacturer ID:").grid(row=0, column=0, sticky="w", padx=5, pady=4)
        self.id_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.id_var, state="disabled", width=10).grid(
            row=0, column=1, sticky="w", padx=5, pady=4
        )

        # ManufacturerName (required, unique)
        ttk.Label(panel, text="Manufacturer Name *:").grid(row=0, column=2, sticky="w", padx=5, pady=4)
        self.name_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.name_var, width=25).grid(
            row=0, column=3, sticky="ew", padx=5, pady=4
        )

        # ShortName
        ttk.Label(panel, text="Short Name:").grid(row=1, column=0, sticky="w", padx=5, pady=4)
        self.short_name_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.short_name_var, width=20).grid(
            row=1, column=1, sticky="ew", padx=5, pady=4
        )

        # Country
        ttk.Label(panel, text="Country:").grid(row=1, column=2, sticky="w", padx=5, pady=4)
        self.country_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.country_var, width=20).grid(
            row=1, column=3, sticky="ew", padx=5, pady=4
        )

        # Website
        ttk.Label(panel, text="Website:").grid(row=2, column=0, sticky="w", padx=5, pady=4)
        self.website_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.website_var, width=25).grid(
            row=2, column=1, columnspan=3, sticky="ew", padx=5, pady=4
        )

        # ContactEmail / ContactPhone
        ttk.Label(panel, text="Contact Email:").grid(row=3, column=0, sticky="w", padx=5, pady=4)
        self.contact_email_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.contact_email_var, width=25).grid(
            row=3, column=1, sticky="ew", padx=5, pady=4
        )

        ttk.Label(panel, text="Contact Phone:").grid(row=3, column=2, sticky="w", padx=5, pady=4)
        self.contact_phone_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.contact_phone_var, width=20).grid(
            row=3, column=3, sticky="ew", padx=5, pady=4
        )

        # LocalRepresentative / LocalRepPhone
        ttk.Label(panel, text="Local Representative:").grid(row=4, column=0, sticky="w", padx=5, pady=4)
        self.local_rep_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.local_rep_var, width=25).grid(
            row=4, column=1, sticky="ew", padx=5, pady=4
        )

        ttk.Label(panel, text="Local Rep Phone:").grid(row=4, column=2, sticky="w", padx=5, pady=4)
        self.local_rep_phone_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.local_rep_phone_var, width=20).grid(
            row=4, column=3, sticky="ew", padx=5, pady=4
        )

        # LocalRepEmail
        ttk.Label(panel, text="Local Rep Email:").grid(row=5, column=0, sticky="w", padx=5, pady=4)
        self.local_rep_email_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.local_rep_email_var, width=25).grid(
            row=5, column=1, sticky="ew", padx=5, pady=4
        )

        # IsApprovedVendor / HasServiceCenter checkboxes
        self.approved_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(panel, text="Approved Vendor", variable=self.approved_var).grid(
            row=5, column=2, sticky="w", padx=5, pady=4
        )
        self.service_center_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(panel, text="Has Service Center", variable=self.service_center_var).grid(
            row=5, column=3, sticky="w", padx=5, pady=4
        )

        # Ratings row
        ttk.Label(panel, text="Quality Rating (0-5):").grid(row=6, column=0, sticky="w", padx=5, pady=4)
        self.quality_rating_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.quality_rating_var, width=10).grid(
            row=6, column=1, sticky="w", padx=5, pady=4
        )

        ttk.Label(panel, text="Delivery Rating (0-5):").grid(row=6, column=2, sticky="w", padx=5, pady=4)
        self.delivery_rating_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.delivery_rating_var, width=10).grid(
            row=6, column=3, sticky="w", padx=5, pady=4
        )

        ttk.Label(panel, text="Tech Support Rating (0-5):").grid(row=7, column=0, sticky="w", padx=5, pady=4)
        self.tech_support_rating_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.tech_support_rating_var, width=10).grid(
            row=7, column=1, sticky="w", padx=5, pady=4
        )

        # Notes (long text -> scrolled Text widget)
        ttk.Label(panel, text="Notes:").grid(row=8, column=0, sticky="nw", padx=5, pady=4)
        notes_frame = ttk.Frame(panel)
        notes_frame.grid(row=8, column=1, columnspan=3, sticky="ew", padx=5, pady=4)
        self.notes_text = tk.Text(notes_frame, height=4, width=50, wrap="word")
        notes_scroll = ttk.Scrollbar(notes_frame, orient="vertical", command=self.notes_text.yview)
        self.notes_text.configure(yscrollcommand=notes_scroll.set)
        self.notes_text.pack(side="left", fill="both", expand=True)
        notes_scroll.pack(side="left", fill="y")

        ttk.Label(panel, text="* Required fields", foreground="gray").grid(
            row=9, column=0, columnspan=2, sticky="w", padx=5, pady=4
        )

        # Action buttons
        action_frame = ttk.Frame(panel)
        action_frame.grid(row=10, column=0, columnspan=4, sticky="e", padx=5, pady=(10, 5))
        ttk.Button(action_frame, text="New", command=self._new_record).pack(side="left", padx=3)
        ttk.Button(action_frame, text="Save", command=self._save_record).pack(side="left", padx=3)
        ttk.Button(action_frame, text="Delete", command=self._delete_record).pack(side="left", padx=3)
        ttk.Button(action_frame, text="Refresh", command=self.refresh_data).pack(side="left", padx=3)

    # ------------------------------------------------------------------
    # Data loading / search
    # ------------------------------------------------------------------
    def refresh_data(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()

            query = """
                SELECT ManufacturerID, ManufacturerName, ShortName, Country,
                       Website, ContactEmail, ContactPhone, LocalRepresentative,
                       LocalRepPhone, LocalRepEmail, IsApprovedVendor,
                       QualityRating, DeliveryRating, TechnicalSupportRating,
                       HasServiceCenter, Notes
                FROM Manufacturers
                WHERE 1 = 1
            """
            params = []

            keyword = self.keyword_var.get().strip()
            if keyword:
                query += """ AND (
                    ManufacturerName LIKE ? OR ShortName LIKE ? OR Country LIKE ?
                    OR ContactEmail LIKE ? OR LocalRepresentative LIKE ?
                )"""
                like = f"%{keyword}%"
                params.extend([like, like, like, like, like])

            approved = self.approved_filter_var.get()
            if approved == "Yes":
                query += " AND IsApprovedVendor = 1"
            elif approved == "No":
                query += " AND IsApprovedVendor = 0"

            service = self.service_filter_var.get()
            if service == "Yes":
                query += " AND HasServiceCenter = 1"
            elif service == "No":
                query += " AND HasServiceCenter = 0"

            min_rating = self.min_rating_var.get().strip()
            if min_rating:
                try:
                    min_rating_val = float(min_rating)
                    query += " AND QualityRating >= ?"
                    params.append(min_rating_val)
                except ValueError:
                    messagebox.showwarning("Validation", "Min Quality Rating must be a number.")
                    conn.close()
                    return

            query += " ORDER BY ManufacturerName"

            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()

            self.tree.delete(*self.tree.get_children())
            self._row_cache = {}
            for row in rows:
                values = list(row)
                display = [
                    values[0], values[1], values[2], values[3],
                    values[5], values[6], values[7],
                    "Yes" if values[10] else "No",
                    values[11], values[12], values[13],
                    "Yes" if values[14] else "No"
                ]
                self._row_cache[str(values[0])] = values
                self.tree.insert("", "end", values=display)

        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to load Manufacturers data:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error while loading data:\n{e}")

    # ------------------------------------------------------------------
    # Selection handling
    # ------------------------------------------------------------------
    def _on_row_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return

        display_values = self.tree.item(selected[0], "values")
        manufacturer_id = str(display_values[0])
        full = self._row_cache.get(manufacturer_id)
        if full is None:
            return

        self.selected_id = full[0]
        self.id_var.set(full[0])
        self.name_var.set(full[1])
        self.short_name_var.set(full[2] or "")
        self.country_var.set(full[3] or "")
        self.website_var.set(full[4] or "")
        self.contact_email_var.set(full[5] or "")
        self.contact_phone_var.set(full[6] or "")
        self.local_rep_var.set(full[7] or "")
        self.local_rep_phone_var.set(full[8] or "")
        self.local_rep_email_var.set(full[9] or "")
        self.approved_var.set(bool(full[10]))
        self.quality_rating_var.set(str(full[11]) if full[11] is not None else "")
        self.delivery_rating_var.set(str(full[12]) if full[12] is not None else "")
        self.tech_support_rating_var.set(str(full[13]) if full[13] is not None else "")
        self.service_center_var.set(bool(full[14]))

        self.notes_text.delete("1.0", tk.END)
        if full[15]:
            self.notes_text.insert("1.0", full[15])

    def _new_record(self):
        self.selected_id = None
        self.tree.selection_remove(self.tree.selection())

        self.id_var.set("")
        self.name_var.set("")
        self.short_name_var.set("")
        self.country_var.set("")
        self.website_var.set("")
        self.contact_email_var.set("")
        self.contact_phone_var.set("")
        self.local_rep_var.set("")
        self.local_rep_phone_var.set("")
        self.local_rep_email_var.set("")
        self.approved_var.set(True)
        self.service_center_var.set(False)
        self.quality_rating_var.set("")
        self.delivery_rating_var.set("")
        self.tech_support_rating_var.set("")
        self.notes_text.delete("1.0", tk.END)

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    def _validate_rating(self, value_str, field_label):
        if not value_str:
            return True, None
        try:
            value = float(value_str)
        except ValueError:
            messagebox.showwarning("Validation", f"{field_label} must be a valid number.")
            return False, None
        if not (0 <= value <= 5):
            messagebox.showwarning("Validation", f"{field_label} must be between 0.00 and 5.00.")
            return False, None
        return True, round(value, 2)

    def _validate_form(self):
        if not self.name_var.get().strip():
            messagebox.showwarning("Validation", "Manufacturer Name is required.")
            return False

        email = self.contact_email_var.get().strip()
        if email and not self.EMAIL_PATTERN.match(email):
            messagebox.showwarning("Validation", "Contact Email is not a valid email address.")
            return False

        rep_email = self.local_rep_email_var.get().strip()
        if rep_email and not self.EMAIL_PATTERN.match(rep_email):
            messagebox.showwarning("Validation", "Local Rep Email is not a valid email address.")
            return False

        for value_str, label in [
            (self.quality_rating_var.get().strip(), "Quality Rating"),
            (self.delivery_rating_var.get().strip(), "Delivery Rating"),
            (self.tech_support_rating_var.get().strip(), "Technical Support Rating"),
        ]:
            ok, _ = self._validate_rating(value_str, label)
            if not ok:
                return False

        return True

    # ------------------------------------------------------------------
    # Save (Insert / Update)
    # ------------------------------------------------------------------
    def _save_record(self):
        if not self._validate_form():
            return

        _, quality = self._validate_rating(self.quality_rating_var.get().strip(), "Quality Rating")
        _, delivery = self._validate_rating(self.delivery_rating_var.get().strip(), "Delivery Rating")
        _, tech_support = self._validate_rating(
            self.tech_support_rating_var.get().strip(), "Technical Support Rating"
        )

        name = self.name_var.get().strip()
        short_name = self.short_name_var.get().strip() or None
        country = self.country_var.get().strip() or None
        website = self.website_var.get().strip() or None
        contact_email = self.contact_email_var.get().strip() or None
        contact_phone = self.contact_phone_var.get().strip() or None
        local_rep = self.local_rep_var.get().strip() or None
        local_rep_phone = self.local_rep_phone_var.get().strip() or None
        local_rep_email = self.local_rep_email_var.get().strip() or None
        is_approved = 1 if self.approved_var.get() else 0
        has_service_center = 1 if self.service_center_var.get() else 0
        notes = self.notes_text.get("1.0", tk.END).strip() or None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            if self.selected_id:
                cursor.execute(
                    """
                    UPDATE Manufacturers
                    SET ManufacturerName = ?, ShortName = ?, Country = ?, Website = ?,
                        ContactEmail = ?, ContactPhone = ?, LocalRepresentative = ?,
                        LocalRepPhone = ?, LocalRepEmail = ?, IsApprovedVendor = ?,
                        QualityRating = ?, DeliveryRating = ?, TechnicalSupportRating = ?,
                        HasServiceCenter = ?, Notes = ?
                    WHERE ManufacturerID = ?
                    """,
                    (name, short_name, country, website, contact_email, contact_phone,
                     local_rep, local_rep_phone, local_rep_email, is_approved,
                     quality, delivery, tech_support, has_service_center, notes,
                     self.selected_id)
                )
                conn.commit()
                messagebox.showinfo("Success", "Manufacturer updated successfully.")
            else:
                cursor.execute(
                    """
                    INSERT INTO Manufacturers
                        (ManufacturerName, ShortName, Country, Website, ContactEmail,
                         ContactPhone, LocalRepresentative, LocalRepPhone, LocalRepEmail,
                         IsApprovedVendor, QualityRating, DeliveryRating,
                         TechnicalSupportRating, HasServiceCenter, Notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (name, short_name, country, website, contact_email, contact_phone,
                     local_rep, local_rep_phone, local_rep_email, is_approved,
                     quality, delivery, tech_support, has_service_center, notes)
                )
                conn.commit()
                messagebox.showinfo("Success", "Manufacturer added successfully.")

            conn.close()
            self.refresh_data()
            self._new_record()

        except pyodbc.IntegrityError as e:
            messagebox.showerror(
                "Integrity Error",
                f"Save failed. This likely violates a unique constraint "
                f"(Manufacturer Name must be unique):\n{e}"
            )
        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to save Manufacturer:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error while saving:\n{e}")

    # ------------------------------------------------------------------
    # Delete (with dynamic FK dependency check)
    # ------------------------------------------------------------------
    def _get_dependent_records(self, conn, manufacturer_id):
        """
        Dynamically discover every table with a FK referencing Manufacturers,
        then count rows that reference this ManufacturerID. Avoids hardcoding
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
                    (manufacturer_id,)
                )
                count = count_cursor.fetchone()[0]
                if count > 0:
                    dependents.append((child_table, count))
            except pyodbc.Error:
                continue

        return dependents

    def _delete_record(self):
        if not self.selected_id:
            messagebox.showwarning("No Selection", "Please select a Manufacturer to delete.")
            return

        try:
            conn = get_connection()
            dependents = self._get_dependent_records(conn, self.selected_id)

            if dependents:
                detail = "\n".join(f"  - {table}: {count} record(s)" for table, count in dependents)
                proceed = messagebox.askyesno(
                    "Manufacturer In Use",
                    f"This Manufacturer is referenced by other records:\n\n{detail}\n\n"
                    "Deleting it may fail or orphan related data depending on your "
                    "database's FK constraints.\n\nDo you still want to attempt deletion?"
                )
                if not proceed:
                    conn.close()
                    return
            else:
                confirm = messagebox.askyesno(
                    "Confirm Delete",
                    f"Delete Manufacturer '{self.name_var.get()}' (ID {self.selected_id})?"
                )
                if not confirm:
                    conn.close()
                    return

            cursor = conn.cursor()
            cursor.execute("DELETE FROM Manufacturers WHERE ManufacturerID = ?", (self.selected_id,))
            conn.commit()
            conn.close()

            messagebox.showinfo("Deleted", "Manufacturer deleted successfully.")
            self.refresh_data()
            self._new_record()

        except pyodbc.IntegrityError as e:
            messagebox.showerror(
                "Integrity Error",
                f"Cannot delete this Manufacturer because other records depend on it:\n{e}"
            )
        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to delete Manufacturer:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error while deleting:\n{e}")
