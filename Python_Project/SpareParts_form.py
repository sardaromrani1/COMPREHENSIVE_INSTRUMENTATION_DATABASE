"""
SpareParts_form.py
CRUD form for the SpareParts table (~80 columns).

Given the size of this table, fields are declared as metadata (FIELD_TABS)
rather than hand-coded one-by-one like the smaller Sites/Manufacturers forms.
This keeps the file maintainable while still producing the same visual
pattern: Treeview list + column-scoped search + detail panel with
Save/New/Delete/Refresh, tkcalendar DateEntry for dates, and a dynamic
FK-dependency check on delete.

Detail panel is organized into a ttk.Notebook (tabs) because 80 columns
can't reasonably fit on one screen - same approach used for the
~140-column Instruments form.

Foreign keys:
- ManufacturerID -> Manufacturers(ManufacturerID, ManufacturerName)
  (ManufacturerName is also stored denormalized on SpareParts per the
  schema comment "Denormalized for quick access" - this form keeps that
  field in sync automatically whenever a Manufacturer is chosen.)
- InstrumentTypeID -> InstrumentTypes(InstrumentTypeID, TypeName)
  ASSUMPTION: the display column on InstrumentTypes is named "TypeName".
  If your actual column is named differently, change DISPLAY_COL below
  in FK_LOOKUP_CONFIG['InstrumentTypeID'] to match.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import pyodbc
import getpass
from datetime import datetime, date

from db_connection import get_connection


# ----------------------------------------------------------------------
# Foreign key lookup configuration
# ----------------------------------------------------------------------
FK_LOOKUP_CONFIG = {
    "ManufacturerID": {
        "table": "Manufacturers",
        "id_col": "ManufacturerID",
        "display_col": "ManufacturerName",
    },
    "InstrumentTypeID": {
        "table": "InstrumentTypes",
        "id_col": "InstrumentTypeID",
        "display_col": "TypeName",  # ASSUMPTION - adjust if actual column differs
    },
}


# ----------------------------------------------------------------------
# Field metadata, organized by tab.
# kind: 'str' | 'choice' | 'int' | 'decimal' | 'bool' | 'date' | 'text' | 'readonly'
# ----------------------------------------------------------------------
FIELD_TABS = [
    ("General", [
        {"db": "PartNumber", "label": "Part Number *", "kind": "str", "width": 25},
        {"db": "ManufacturerPartNumber", "label": "Manufacturer Part No.", "kind": "str", "width": 25},
        {"db": "AlternatePartNumber", "label": "Alternate Part No.", "kind": "str", "width": 25},
        {"db": "PartName", "label": "Part Name *", "kind": "str", "width": 35},
        {"db": "PartCategory", "label": "Part Category", "kind": "choice", "width": 20,
         "choices": ["Sensor", "Transmitter", "Electronics", "Housing", "Gasket", "Diaphragm", "Other"]},
        {"db": "PartSubCategory", "label": "Part Sub-Category", "kind": "str", "width": 20},
        {"db": "PartType", "label": "Part Type", "kind": "choice", "width": 18,
         "choices": ["Consumable", "Repairable", "Critical", "Insurance"]},
        {"db": "Description", "label": "Description", "kind": "text", "height": 3},
    ]),
    ("Manufacturer / Compatibility", [
        # ManufacturerID and InstrumentTypeID are handled specially (FK combos)
        {"db": "CompatibleModels", "label": "Compatible Models", "kind": "str", "width": 40},
        {"db": "CompatibleTags", "label": "Compatible Tags", "kind": "text", "height": 3},
        {"db": "Interchangeable", "label": "Interchangeable", "kind": "bool", "default": False},
        {"db": "InterchangeableWith", "label": "Interchangeable With", "kind": "str", "width": 40},
    ]),
    ("Technical", [
        {"db": "TechnicalSpecs", "label": "Technical Specs", "kind": "text", "height": 5},
        {"db": "Material", "label": "Material", "kind": "str", "width": 25},
        {"db": "Dimensions", "label": "Dimensions (L x W x H)", "kind": "str", "width": 25},
        {"db": "Weight_Kg", "label": "Weight (Kg)", "kind": "decimal", "width": 12, "min": 0},
    ]),
    ("Procurement", [
        {"db": "UnitOfMeasure", "label": "Unit of Measure", "kind": "choice", "width": 15,
         "choices": ["Each", "Set", "Meter", "Liter", "Kg", "Box", "Roll", "Pair"]},
        {"db": "UnitCost", "label": "Unit Cost", "kind": "decimal", "width": 14, "min": 0},
        {"db": "Currency", "label": "Currency", "kind": "choice", "width": 10,
         "choices": ["USD", "EUR", "GBP", "IRR"], "default": "USD"},
        {"db": "LastPurchasePrice", "label": "Last Purchase Price", "kind": "decimal", "width": 14, "min": 0},
        {"db": "LastPurchaseDate", "label": "Last Purchase Date", "kind": "date"},
        {"db": "PriceValidUntil", "label": "Price Valid Until", "kind": "date"},
        {"db": "PrimarySupplier", "label": "Primary Supplier", "kind": "str", "width": 25},
        {"db": "PrimarySupplierContact", "label": "Primary Supplier Contact", "kind": "str", "width": 25},
        {"db": "AlternativeSupplier1", "label": "Alternative Supplier 1", "kind": "str", "width": 25},
        {"db": "AlternativeSupplier2", "label": "Alternative Supplier 2", "kind": "str", "width": 25},
    ]),
    ("Lead Time / Inventory", [
        {"db": "LeadTime_Days", "label": "Lead Time (Days)", "kind": "int", "width": 10, "min": 0},
        {"db": "LeadTimeCategory", "label": "Lead Time Category", "kind": "choice", "width": 15,
         "choices": ["Stock", "Short", "Medium", "Long", "Critical"]},
        {"db": "EmergencyProcurement", "label": "Emergency Procurement", "kind": "bool", "default": False},
        {"db": "EmergencySupplier", "label": "Emergency Supplier", "kind": "str", "width": 25},
        {"db": "MinStockLevel", "label": "Min Stock Level", "kind": "int", "width": 10, "min": 0, "default": 0},
        {"db": "MaxStockLevel", "label": "Max Stock Level", "kind": "int", "width": 10, "min": 0},
        {"db": "ReorderPoint", "label": "Reorder Point", "kind": "int", "width": 10, "min": 0},
        {"db": "ReorderQuantity", "label": "Reorder Quantity", "kind": "int", "width": 10, "min": 0},
        {"db": "SafetyStock", "label": "Safety Stock", "kind": "int", "width": 10, "min": 0, "default": 0},
        {"db": "EconomicOrderQuantity", "label": "EOQ", "kind": "int", "width": 10, "min": 0},
    ]),
    ("Usage / Criticality", [
        {"db": "AnnualUsage", "label": "Annual Usage", "kind": "int", "width": 10, "min": 0, "default": 0},
        {"db": "AverageMonthlyUsage", "label": "Avg Monthly Usage", "kind": "decimal", "width": 10, "min": 0, "default": 0},
        {"db": "LastUsedDate", "label": "Last Used Date", "kind": "date"},
        {"db": "UsageFrequency", "label": "Usage Frequency", "kind": "choice", "width": 15,
         "choices": ["Daily", "Weekly", "Monthly", "Quarterly", "Rarely"]},
        {"db": "Criticality", "label": "Criticality", "kind": "choice", "width": 12,
         "choices": ["Low", "Medium", "High", "Critical"], "default": "Medium"},
        {"db": "IsInsuranceSpare", "label": "Insurance Spare", "kind": "bool", "default": False},
        {"db": "IsCriticalSpare", "label": "Critical Spare", "kind": "bool", "default": False},
        {"db": "IsLongLeadItem", "label": "Long Lead Item", "kind": "bool", "default": False},
    ]),
    ("Shelf Life / Quality", [
        {"db": "HasShelfLife", "label": "Has Shelf Life", "kind": "bool", "default": False},
        {"db": "ShelfLife_Months", "label": "Shelf Life (Months)", "kind": "int", "width": 10, "min": 0},
        {"db": "RequiresSpecialStorage", "label": "Requires Special Storage", "kind": "bool", "default": False},
        {"db": "StorageConditions", "label": "Storage Conditions", "kind": "text", "height": 3},
        {"db": "RequiresCertification", "label": "Requires Certification", "kind": "bool", "default": False},
        {"db": "CertificationType", "label": "Certification Type", "kind": "str", "width": 25},
        {"db": "QualityStandard", "label": "Quality Standard", "kind": "str", "width": 20},
    ]),
    ("Obsolescence / Warranty", [
        {"db": "IsObsolete", "label": "Obsolete", "kind": "bool", "default": False},
        {"db": "ObsolescenceDate", "label": "Obsolescence Date", "kind": "date"},
        {"db": "ObsolescenceReason", "label": "Obsolescence Reason", "kind": "text", "height": 3},
        {"db": "ReplacementPartNumber", "label": "Replacement Part No.", "kind": "str", "width": 25},
        {"db": "WarrantyPeriod_Months", "label": "Warranty Period (Months)", "kind": "int", "width": 10, "min": 0},
        {"db": "WarrantyTerms", "label": "Warranty Terms", "kind": "text", "height": 3},
    ]),
    ("Documentation / HSE", [
        {"db": "DatasheetPath", "label": "Datasheet Path", "kind": "str", "width": 40},
        {"db": "DrawingPath", "label": "Drawing Path", "kind": "str", "width": 40},
        {"db": "ImagePath", "label": "Image Path", "kind": "str", "width": 40},
        {"db": "CertificatePath", "label": "Certificate Path", "kind": "str", "width": 40},
        {"db": "IsHazardousMaterial", "label": "Hazardous Material", "kind": "bool", "default": False},
        {"db": "MSDS_Path", "label": "MSDS Path", "kind": "str", "width": 40},
        {"db": "HandlingInstructions", "label": "Handling Instructions", "kind": "text", "height": 3},
        {"db": "DisposalRequirements", "label": "Disposal Requirements", "kind": "text", "height": 3},
    ]),
    ("Tracking / Status", [
        {"db": "CreatedBy", "label": "Created By", "kind": "readonly"},
        {"db": "CreatedDate", "label": "Created Date", "kind": "readonly"},
        {"db": "ModifiedBy", "label": "Modified By", "kind": "readonly"},
        {"db": "ModifiedDate", "label": "Modified Date", "kind": "readonly"},
        {"db": "LastReviewDate", "label": "Last Review Date", "kind": "date"},
        {"db": "NextReviewDate", "label": "Next Review Date", "kind": "date"},
        {"db": "IsActive", "label": "Active", "kind": "bool", "default": True},
        {"db": "IsApproved", "label": "Approved", "kind": "bool", "default": False},
        {"db": "ApprovedBy", "label": "Approved By", "kind": "str", "width": 20},
        {"db": "ApprovalDate", "label": "Approval Date", "kind": "date"},
    ]),
    ("Notes", [
        {"db": "Notes", "label": "Notes", "kind": "text", "height": 10},
    ]),
]


class SparePartsForm(ttk.Frame):

    TABLE_NAME = "SpareParts"
    PK_COLUMN = "SparePartID"

    def __init__(self, parent):
        super().__init__(parent)
        self.selected_id = None

        # Widget/variable registries, keyed by db column name
        self.str_vars = {}       # 'str' / 'choice' / 'int' / 'decimal' entries -> StringVar
        self.bool_vars = {}      # 'bool' -> BooleanVar
        self.text_widgets = {}   # 'text' -> tk.Text
        self.date_state = {}     # 'date' -> (BooleanVar set_flag, DateEntry widget)
        self.readonly_vars = {}  # 'readonly' -> StringVar (system-managed, display only)

        # FK combo state
        self.manufacturer_lookup = {}   # display string -> ManufacturerID
        self.instrument_type_lookup = {}  # display string -> InstrumentTypeID
        self.manufacturer_var = tk.StringVar()
        self.instrument_type_var = tk.StringVar()
        self.manufacturer_name_display = tk.StringVar()  # read-only denormalized name

        self._build_ui()
        self._load_fk_lookups()
        self.refresh_data()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------
    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        title = ttk.Label(self, text="Spare Parts", font=("Segoe UI", 14, "bold"))
        title.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 5))

        self._build_search_bar()
        self._build_treeview()
        self._build_detail_panel()

    # -- Search bar -------------------------------------------------------
    def _build_search_bar(self):
        bar = ttk.LabelFrame(self, text="Search")
        bar.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        for c in range(8):
            bar.columnconfigure(c, weight=1)

        ttk.Label(bar, text="Keyword:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.keyword_var = tk.StringVar()
        ttk.Entry(bar, textvariable=self.keyword_var).grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(bar, text="Category:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.category_filter_var = tk.StringVar()
        ttk.Entry(bar, textvariable=self.category_filter_var, width=15).grid(
            row=0, column=3, sticky="ew", padx=5, pady=5
        )

        ttk.Label(bar, text="Manufacturer:").grid(row=0, column=4, sticky="w", padx=5, pady=5)
        self.manufacturer_filter_var = tk.StringVar()
        self.manufacturer_filter_combo = ttk.Combobox(
            bar, textvariable=self.manufacturer_filter_var, state="readonly", width=20
        )
        self.manufacturer_filter_combo.grid(row=0, column=5, sticky="ew", padx=5, pady=5)

        ttk.Label(bar, text="Criticality:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.criticality_filter_var = tk.StringVar()
        crit_combo = ttk.Combobox(
            bar, textvariable=self.criticality_filter_var, state="readonly", width=12,
            values=["(All)", "Low", "Medium", "High", "Critical"]
        )
        crit_combo.current(0)
        crit_combo.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(bar, text="Active:").grid(row=1, column=2, sticky="w", padx=5, pady=5)
        self.active_filter_var = tk.StringVar()
        active_combo = ttk.Combobox(
            bar, textvariable=self.active_filter_var, state="readonly", width=10,
            values=["(All)", "Yes", "No"]
        )
        active_combo.current(0)
        active_combo.grid(row=1, column=3, sticky="w", padx=5, pady=5)

        ttk.Label(bar, text="Obsolete:").grid(row=1, column=4, sticky="w", padx=5, pady=5)
        self.obsolete_filter_var = tk.StringVar()
        obsolete_combo = ttk.Combobox(
            bar, textvariable=self.obsolete_filter_var, state="readonly", width=10,
            values=["(All)", "Yes", "No"]
        )
        obsolete_combo.current(0)
        obsolete_combo.grid(row=1, column=5, sticky="w", padx=5, pady=5)

        btn_frame = ttk.Frame(bar)
        btn_frame.grid(row=1, column=6, columnspan=2, sticky="e", padx=5, pady=5)
        ttk.Button(btn_frame, text="Search", command=self.refresh_data).pack(side="left", padx=3)
        ttk.Button(btn_frame, text="Clear", command=self._clear_search).pack(side="left", padx=3)

    def _clear_search(self):
        self.keyword_var.set("")
        self.category_filter_var.set("")
        self.manufacturer_filter_var.set("(All)")
        self.criticality_filter_var.set("(All)")
        self.active_filter_var.set("(All)")
        self.obsolete_filter_var.set("(All)")
        self.refresh_data()

    # -- Treeview -----------------------------------------------------------
    def _build_treeview(self):
        frame = ttk.Frame(self)
        frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        columns = (
            "SparePartID", "PartNumber", "PartName", "PartCategory",
            "ManufacturerName", "Criticality", "MinStockLevel",
            "ReorderPoint", "LeadTime_Days", "IsActive", "IsObsolete"
        )
        self.tree = ttk.Treeview(frame, columns=columns, show="headings", height=12)

        headings = {
            "SparePartID": "ID", "PartNumber": "Part Number", "PartName": "Part Name",
            "PartCategory": "Category", "ManufacturerName": "Manufacturer",
            "Criticality": "Criticality", "MinStockLevel": "Min Stock",
            "ReorderPoint": "Reorder Pt", "LeadTime_Days": "Lead Time (d)",
            "IsActive": "Active", "IsObsolete": "Obsolete"
        }
        widths = {
            "SparePartID": 50, "PartNumber": 120, "PartName": 180,
            "PartCategory": 100, "ManufacturerName": 130, "Criticality": 80,
            "MinStockLevel": 70, "ReorderPoint": 70, "LeadTime_Days": 80,
            "IsActive": 60, "IsObsolete": 70
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

    # -- Detail panel (Notebook with tabs) ----------------------------------
    def _build_detail_panel(self):
        outer = ttk.LabelFrame(self, text="Spare Part Details")
        outer.grid(row=3, column=0, sticky="nsew", padx=10, pady=(5, 10))
        self.rowconfigure(3, weight=0)
        outer.columnconfigure(0, weight=1)

        # PK + FK row shown above the tabs (always visible regardless of tab)
        top_row = ttk.Frame(outer)
        top_row.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        for c in range(6):
            top_row.columnconfigure(c, weight=1)

        ttk.Label(top_row, text="Spare Part ID:").grid(row=0, column=0, sticky="w", padx=5, pady=3)
        self.id_var = tk.StringVar()
        ttk.Entry(top_row, textvariable=self.id_var, state="disabled", width=10).grid(
            row=0, column=1, sticky="w", padx=5, pady=3
        )

        ttk.Label(top_row, text="Manufacturer:").grid(row=0, column=2, sticky="w", padx=5, pady=3)
        self.manufacturer_combo = ttk.Combobox(
            top_row, textvariable=self.manufacturer_var, state="readonly", width=25
        )
        self.manufacturer_combo.grid(row=0, column=3, sticky="ew", padx=5, pady=3)
        self.manufacturer_combo.bind("<<ComboboxSelected>>", self._on_manufacturer_selected)

        ttk.Label(top_row, text="Instrument Type:").grid(row=0, column=4, sticky="w", padx=5, pady=3)
        self.instrument_type_combo = ttk.Combobox(
            top_row, textvariable=self.instrument_type_var, state="readonly", width=25
        )
        self.instrument_type_combo.grid(row=0, column=5, sticky="ew", padx=5, pady=3)

        ttk.Button(top_row, text="Reload Lookups", command=self._load_fk_lookups).grid(
            row=1, column=5, sticky="e", padx=5, pady=3
        )

        # Notebook with the tabbed field groups
        self.notebook = ttk.Notebook(outer)
        self.notebook.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        outer.rowconfigure(1, weight=1)

        for tab_title, fields in FIELD_TABS:
            tab_frame = self._build_tab(self.notebook, fields)
            self.notebook.add(tab_frame, text=tab_title)

        ttk.Label(outer, text="* Required fields", foreground="gray").grid(
            row=2, column=0, sticky="w", padx=10, pady=(0, 5)
        )

        # Action buttons
        action_frame = ttk.Frame(outer)
        action_frame.grid(row=3, column=0, sticky="e", padx=10, pady=(0, 10))
        ttk.Button(action_frame, text="New", command=self._new_record).pack(side="left", padx=3)
        ttk.Button(action_frame, text="Save", command=self._save_record).pack(side="left", padx=3)
        ttk.Button(action_frame, text="Delete", command=self._delete_record).pack(side="left", padx=3)
        ttk.Button(action_frame, text="Refresh", command=self.refresh_data).pack(side="left", padx=3)

    def _build_tab(self, notebook, fields):
        """Builds one notebook tab from a list of field-spec dicts, 2 fields per row."""
        outer_frame = ttk.Frame(notebook)

        canvas = tk.Canvas(outer_frame, highlightthickness=0)
        vsb = ttk.Scrollbar(outer_frame, orient="vertical", command=canvas.yview)
        inner = ttk.Frame(canvas)

        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=vsb.set)

        canvas.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        for c in range(4):
            inner.columnconfigure(c, weight=1)

        row = 0
        col = 0
        for spec in fields:
            kind = spec["kind"]
            db = spec["db"]
            label = spec["label"]

            # Text and readonly fields span the full row width
            if kind in ("text",):
                ttk.Label(inner, text=label + ":").grid(row=row, column=0, sticky="nw", padx=5, pady=4)
                txt_frame = ttk.Frame(inner)
                txt_frame.grid(row=row, column=1, columnspan=3, sticky="ew", padx=5, pady=4)
                height = spec.get("height", 3)
                txt = tk.Text(txt_frame, height=height, width=50, wrap="word")
                scroll = ttk.Scrollbar(txt_frame, orient="vertical", command=txt.yview)
                txt.configure(yscrollcommand=scroll.set)
                txt.pack(side="left", fill="both", expand=True)
                scroll.pack(side="right", fill="y")
                self.text_widgets[db] = txt
                row += 1
                col = 0
                continue

            if kind == "readonly":
                ttk.Label(inner, text=label + ":").grid(row=row, column=col, sticky="w", padx=5, pady=4)
                var = tk.StringVar()
                ttk.Entry(inner, textvariable=var, state="disabled", width=25).grid(
                    row=row, column=col + 1, sticky="w", padx=5, pady=4
                )
                self.readonly_vars[db] = var
                col += 2
                if col >= 4:
                    col = 0
                    row += 1
                continue

            if kind == "bool":
                var = tk.BooleanVar(value=spec.get("default", False))
                ttk.Checkbutton(inner, text=label, variable=var).grid(
                    row=row, column=col, sticky="w", padx=5, pady=4
                )
                self.bool_vars[db] = var
                col += 1
                if col >= 4:
                    col = 0
                    row += 1
                continue

            if kind == "date":
                ttk.Label(inner, text=label + ":").grid(row=row, column=col, sticky="w", padx=5, pady=4)
                date_frame = ttk.Frame(inner)
                date_frame.grid(row=row, column=col + 1, sticky="w", padx=5, pady=4)
                set_var = tk.BooleanVar(value=False)
                date_widget = DateEntry(date_frame, date_pattern="yyyy-mm-dd", width=11, state="disabled")

                def toggle(dw=date_widget, sv=set_var):
                    dw.configure(state="normal" if sv.get() else "disabled")

                ttk.Checkbutton(date_frame, text="Set", variable=set_var, command=toggle).pack(side="left")
                date_widget.pack(side="left", padx=5)
                self.date_state[db] = (set_var, date_widget)
                col += 2
                if col >= 4:
                    col = 0
                    row += 1
                continue

            # 'str', 'choice', 'int', 'decimal' -> Entry or Combobox, StringVar-backed
            ttk.Label(inner, text=label + ":").grid(row=row, column=col, sticky="w", padx=5, pady=4)
            var = tk.StringVar(value=str(spec.get("default", "")) if spec.get("default") is not None else "")
            width = spec.get("width", 20)

            if kind == "choice":
                widget = ttk.Combobox(inner, textvariable=var, values=spec.get("choices", []), width=width)
            else:
                widget = ttk.Entry(inner, textvariable=var, width=width)

            widget.grid(row=row, column=col + 1, sticky="ew", padx=5, pady=4)
            self.str_vars[db] = var

            col += 2
            if col >= 4:
                col = 0
                row += 1

        return outer_frame

    # ------------------------------------------------------------------
    # FK lookups
    # ------------------------------------------------------------------
    def _load_fk_lookups(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()

            # Manufacturers
            cursor.execute("SELECT ManufacturerID, ManufacturerName FROM Manufacturers ORDER BY ManufacturerName")
            self.manufacturer_lookup = {}
            display_values = []
            for mid, name in cursor.fetchall():
                display = f"{name} (ID {mid})"
                self.manufacturer_lookup[display] = mid
                display_values.append(display)
            self.manufacturer_combo["values"] = display_values
            self.manufacturer_filter_combo["values"] = ["(All)"] + [
                name for name in [d.split(" (ID")[0] for d in display_values]
            ]
            if not self.manufacturer_filter_var.get():
                self.manufacturer_filter_var.set("(All)")

            # Instrument Types
            cursor.execute(
                f"SELECT InstrumentTypeID, {FK_LOOKUP_CONFIG['InstrumentTypeID']['display_col']} "
                f"FROM InstrumentTypes ORDER BY {FK_LOOKUP_CONFIG['InstrumentTypeID']['display_col']}"
            )
            self.instrument_type_lookup = {}
            type_display_values = []
            for tid, name in cursor.fetchall():
                display = f"{name} (ID {tid})"
                self.instrument_type_lookup[display] = tid
                type_display_values.append(display)
            self.instrument_type_combo["values"] = type_display_values

            conn.close()

        except pyodbc.Error as e:
            messagebox.showerror(
                "Database Error",
                f"Failed to load lookup data (Manufacturers / InstrumentTypes):\n{e}"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error while loading lookups:\n{e}")

    def _on_manufacturer_selected(self, event):
        display = self.manufacturer_var.get()
        manufacturer_id = self.manufacturer_lookup.get(display)
        if manufacturer_id is not None:
            # Keep the denormalized ManufacturerName field in sync
            name = display.split(" (ID")[0]
            self.manufacturer_name_display.set(name)

    # ------------------------------------------------------------------
    # Data loading / search
    # ------------------------------------------------------------------
    def refresh_data(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()

            query = """
                SELECT SparePartID, PartNumber, PartName, PartCategory,
                       ManufacturerName, Criticality, MinStockLevel,
                       ReorderPoint, LeadTime_Days, IsActive, IsObsolete
                FROM SpareParts
                WHERE 1 = 1
            """
            params = []

            keyword = self.keyword_var.get().strip()
            if keyword:
                query += """ AND (
                    PartNumber LIKE ? OR PartName LIKE ? OR ManufacturerPartNumber LIKE ?
                    OR CompatibleTags LIKE ? OR Description LIKE ?
                )"""
                like = f"%{keyword}%"
                params.extend([like, like, like, like, like])

            category = self.category_filter_var.get().strip()
            if category:
                query += " AND PartCategory LIKE ?"
                params.append(f"%{category}%")

            manufacturer = self.manufacturer_filter_var.get()
            if manufacturer and manufacturer != "(All)":
                query += " AND ManufacturerName = ?"
                params.append(manufacturer)

            criticality = self.criticality_filter_var.get()
            if criticality and criticality != "(All)":
                query += " AND Criticality = ?"
                params.append(criticality)

            active = self.active_filter_var.get()
            if active == "Yes":
                query += " AND IsActive = 1"
            elif active == "No":
                query += " AND IsActive = 0"

            obsolete = self.obsolete_filter_var.get()
            if obsolete == "Yes":
                query += " AND IsObsolete = 1"
            elif obsolete == "No":
                query += " AND IsObsolete = 0"

            query += " ORDER BY PartNumber"

            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()

            self.tree.delete(*self.tree.get_children())
            for row in rows:
                values = list(row)
                values[9] = "Yes" if values[9] else "No"    # IsActive
                values[10] = "Yes" if values[10] else "No"  # IsObsolete
                self.tree.insert("", "end", values=values)

        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to load Spare Parts data:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error while loading data:\n{e}")

    # ------------------------------------------------------------------
    # Selection handling
    # ------------------------------------------------------------------
    def _all_db_columns(self):
        """All non-PK, non-FK columns declared in FIELD_TABS, in a flat list."""
        cols = []
        for _, fields in FIELD_TABS:
            for spec in fields:
                cols.append(spec["db"])
        return cols

    def _on_row_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return

        values = self.tree.item(selected[0], "values")
        self.selected_id = values[0]

        try:
            conn = get_connection()
            cursor = conn.cursor()

            all_cols = self._all_db_columns() + ["ManufacturerID", "InstrumentTypeID", "ManufacturerName"]
            col_list = ", ".join(f"[{c}]" for c in all_cols)
            cursor.execute(f"SELECT {col_list} FROM SpareParts WHERE SparePartID = ?", (self.selected_id,))
            row = cursor.fetchone()
            conn.close()

            if row is None:
                return

            row_dict = dict(zip(all_cols, row))
            self.id_var.set(self.selected_id)
            self._load_row_into_form(row_dict)

        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to load Spare Part details:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error while loading details:\n{e}")

    def _load_row_into_form(self, row_dict):
        # FK combos
        manufacturer_id = row_dict.get("ManufacturerID")
        if manufacturer_id is not None:
            match = next(
                (disp for disp, mid in self.manufacturer_lookup.items() if mid == manufacturer_id), ""
            )
            self.manufacturer_var.set(match)
        else:
            self.manufacturer_var.set("")
        self.manufacturer_name_display.set(row_dict.get("ManufacturerName") or "")

        instrument_type_id = row_dict.get("InstrumentTypeID")
        if instrument_type_id is not None:
            match = next(
                (disp for disp, tid in self.instrument_type_lookup.items() if tid == instrument_type_id), ""
            )
            self.instrument_type_var.set(match)
        else:
            self.instrument_type_var.set("")

        # Generic fields
        for db, var in self.str_vars.items():
            val = row_dict.get(db)
            var.set("" if val is None else str(val))

        for db, var in self.bool_vars.items():
            var.set(bool(row_dict.get(db)))

        for db, txt in self.text_widgets.items():
            txt.delete("1.0", "end")
            val = row_dict.get(db)
            if val:
                txt.insert("1.0", val)

        for db, (set_var, widget) in self.date_state.items():
            val = row_dict.get(db)
            if val:
                set_var.set(True)
                widget.configure(state="normal")
                if isinstance(val, datetime):
                    val = val.date()
                widget.set_date(val)
            else:
                set_var.set(False)
                widget.configure(state="disabled")

        for db, var in self.readonly_vars.items():
            val = row_dict.get(db)
            var.set("" if val is None else str(val))

    def _new_record(self):
        self.selected_id = None
        self.tree.selection_remove(self.tree.selection())

        self.id_var.set("")
        self.manufacturer_var.set("")
        self.instrument_type_var.set("")
        self.manufacturer_name_display.set("")

        for spec_list in FIELD_TABS:
            pass  # defaults are re-applied below by iterating the registries

        for db, var in self.str_vars.items():
            var.set("")
        # Re-apply declared defaults for choice/int fields
        for _, fields in FIELD_TABS:
            for spec in fields:
                if spec["db"] in self.str_vars and spec.get("default") is not None:
                    self.str_vars[spec["db"]].set(str(spec["default"]))

        for db, var in self.bool_vars.items():
            var.set(False)
        for _, fields in FIELD_TABS:
            for spec in fields:
                if spec["db"] in self.bool_vars and "default" in spec:
                    self.bool_vars[spec["db"]].set(spec["default"])

        for db, txt in self.text_widgets.items():
            txt.delete("1.0", "end")

        for db, (set_var, widget) in self.date_state.items():
            set_var.set(False)
            widget.configure(state="disabled")

        for db, var in self.readonly_vars.items():
            var.set("")

    # ------------------------------------------------------------------
    # Validation / value collection
    # ------------------------------------------------------------------
    def _collect_form_values(self):
        """
        Validates and converts every field into a dict of db_column -> python value,
        ready for INSERT/UPDATE parameter binding. Returns None if validation fails
        (a messagebox has already been shown in that case).
        """
        values = {}

        # Required fields
        part_number = self.str_vars.get("PartNumber")
        part_name = self.str_vars.get("PartName")
        if not part_number.get().strip():
            messagebox.showwarning("Validation", "Part Number is required.")
            return None
        if not part_name.get().strip():
            messagebox.showwarning("Validation", "Part Name is required.")
            return None

        for _, fields in FIELD_TABS:
            for spec in fields:
                db = spec["db"]
                kind = spec["kind"]

                if kind in ("str", "choice"):
                    val = self.str_vars[db].get().strip()
                    values[db] = val or None

                elif kind == "int":
                    val = self.str_vars[db].get().strip()
                    if not val:
                        values[db] = None
                        continue
                    try:
                        ival = int(val)
                    except ValueError:
                        messagebox.showwarning("Validation", f"{spec['label']} must be a whole number.")
                        return None
                    min_v = spec.get("min")
                    if min_v is not None and ival < min_v:
                        messagebox.showwarning("Validation", f"{spec['label']} must be at least {min_v}.")
                        return None
                    values[db] = ival

                elif kind == "decimal":
                    val = self.str_vars[db].get().strip()
                    if not val:
                        values[db] = None
                        continue
                    try:
                        fval = float(val)
                    except ValueError:
                        messagebox.showwarning("Validation", f"{spec['label']} must be a valid number.")
                        return None
                    min_v = spec.get("min")
                    if min_v is not None and fval < min_v:
                        messagebox.showwarning("Validation", f"{spec['label']} must be at least {min_v}.")
                        return None
                    values[db] = fval

                elif kind == "bool":
                    values[db] = 1 if self.bool_vars[db].get() else 0

                elif kind == "text":
                    val = self.text_widgets[db].get("1.0", "end").strip()
                    values[db] = val or None

                elif kind == "date":
                    set_var, widget = self.date_state[db]
                    values[db] = widget.get_date() if set_var.get() else None

                # 'readonly' fields are system-managed - handled separately in save

        # FK fields
        manufacturer_display = self.manufacturer_var.get()
        values["ManufacturerID"] = self.manufacturer_lookup.get(manufacturer_display)
        values["ManufacturerName"] = (
            manufacturer_display.split(" (ID")[0] if manufacturer_display else None
        )

        instrument_type_display = self.instrument_type_var.get()
        values["InstrumentTypeID"] = self.instrument_type_lookup.get(instrument_type_display)

        return values

    # ------------------------------------------------------------------
    # Save (Insert / Update)
    # ------------------------------------------------------------------
    def _save_record(self):
        values = self._collect_form_values()
        if values is None:
            return

        now = datetime.now()
        current_user = getpass.getuser()

        try:
            conn = get_connection()
            cursor = conn.cursor()

            if self.selected_id:
                values["ModifiedBy"] = current_user
                values["ModifiedDate"] = now

                set_clause = ", ".join(f"[{col}] = ?" for col in values.keys())
                params = list(values.values()) + [self.selected_id]
                cursor.execute(
                    f"UPDATE SpareParts SET {set_clause} WHERE SparePartID = ?",
                    params
                )
                conn.commit()
                messagebox.showinfo("Success", "Spare Part updated successfully.")
            else:
                values["CreatedBy"] = current_user
                values["CreatedDate"] = now

                col_list = ", ".join(f"[{col}]" for col in values.keys())
                placeholders = ", ".join("?" for _ in values)
                cursor.execute(
                    f"INSERT INTO SpareParts ({col_list}) VALUES ({placeholders})",
                    list(values.values())
                )
                conn.commit()
                messagebox.showinfo("Success", "Spare Part added successfully.")

            conn.close()
            self.refresh_data()
            self._new_record()

        except pyodbc.IntegrityError as e:
            messagebox.showerror(
                "Integrity Error",
                f"Save failed. This likely violates a unique constraint "
                f"(Part Number must be unique):\n{e}"
            )
        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to save Spare Part:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error while saving:\n{e}")

    # ------------------------------------------------------------------
    # Delete (with dynamic FK dependency check)
    # ------------------------------------------------------------------
    def _get_dependent_records(self, conn, spare_part_id):
        """
        Dynamically discover every table with a FK referencing SpareParts
        (e.g. SparePartUsage), then count rows referencing this SparePartID.
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
                    (spare_part_id,)
                )
                count = count_cursor.fetchone()[0]
                if count > 0:
                    dependents.append((child_table, count))
            except pyodbc.Error:
                continue

        return dependents

    def _delete_record(self):
        if not self.selected_id:
            messagebox.showwarning("No Selection", "Please select a Spare Part to delete.")
            return

        try:
            conn = get_connection()
            dependents = self._get_dependent_records(conn, self.selected_id)

            if dependents:
                detail = "\n".join(f"  - {table}: {count} record(s)" for table, count in dependents)
                proceed = messagebox.askyesno(
                    "Spare Part In Use",
                    f"This Spare Part is referenced by other records:\n\n{detail}\n\n"
                    "Deleting it may fail or orphan related data depending on your "
                    "database's FK constraints.\n\nDo you still want to attempt deletion?"
                )
                if not proceed:
                    conn.close()
                    return
            else:
                confirm = messagebox.askyesno(
                    "Confirm Delete",
                    f"Delete Spare Part '{self.str_vars['PartNumber'].get()}' (ID {self.selected_id})?"
                )
                if not confirm:
                    conn.close()
                    return

            cursor = conn.cursor()
            cursor.execute("DELETE FROM SpareParts WHERE SparePartID = ?", (self.selected_id,))
            conn.commit()
            conn.close()

            messagebox.showinfo("Deleted", "Spare Part deleted successfully.")
            self.refresh_data()
            self._new_record()

        except pyodbc.IntegrityError as e:
            messagebox.showerror(
                "Integrity Error",
                f"Cannot delete this Spare Part because other records depend on it:\n{e}"
            )
        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to delete Spare Part:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error while deleting:\n{e}")
