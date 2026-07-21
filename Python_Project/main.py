"""
main.py

Entry point for the Comprehensive Instrumentation Database desktop application.

DESIGN DIRECTION
-----------------
SCADA / DCS control-room panel aesthetic:
    - Graphite/near-black sidebar and header.
    - Sidebar items grouped into real categories (Master Data / Instrumentation
      / Alarms & Safety), each with its own indicator color - the colored
      squares encode grouping, not decoration.
    - Amber (#ffa726) = primary navigation / "live" indicator.
    - Teal (#00bcd4) = Master Data category.
    - Red (#e53935) = Alarms & Safety category / destructive actions.
    - Green (#43a047) = Save / operational-good actions.
    - A header status pill ("SYSTEM ONLINE") blinks its indicator dot gently.
    - A single global ttk.Style() is configured here for TButton, TEntry,
      TCombobox, Treeview, TNotebook, etc. Every form uses plain ttk widgets
      with no per-widget style overrides, so they all inherit this
      bold/colorful styling automatically - no form file needed editing.

ARCHITECTURE
------------
    - main.py owns the window, sidebar navigation, and content area.
    - It never touches form internals - each form module is a self-contained
      ttk.Frame subclass responsible for its own DB access, layout, and CRUD.
    - SIDEBAR_ITEMS is a simple (label, FormClass, category) list.

NOTE ON CLASS NAMES:
    InstrumentStatus, ControlSystems, Instruments, InstrumentLifecycle,
    SparePartUsage, and AlarmConfiguration use the class names generated in
    this session (InstrumentStatusForm, ControlSystemsForm, InstrumentsForm,
    InstrumentLifecycleForm, SparePartUsageForm, AlarmConfigurationForm).
    Sites, SubSystems, ProcessUnits, Manufacturers, and SpareParts are
    imported using the same "<TableName>Form" naming convention for
    consistency. If any existing file uses a different class name, adjust
    that one import line - nothing else needs to change.

THIS BUILD INCLUDES ONLY:
    Sites, Process Units, Sub-Systems, Control Systems, Manufacturers,
    Instrument Status, Instruments, Instrument Lifecycle, Spare Parts,
    Spare Part Usage, Maintenance Records, Failure Records,
    Alarm Configuration.
    (CalibrationRecords, CalibrationTestPoints, TripInstruments,
    TripsInterlocks, and InstrumentTypes were built earlier this session but
    are NOT wired in here, per the explicit list requested.)
"""

import sys
import tkinter as tk
from tkinter import ttk

# ---- High-DPI awareness on Windows ----
if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            import ctypes
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

# ---- Form imports ----
from Sites_form import SitesForm
from ProcessUnits_form import ProcessUnitsForm
from SubSystems_form import SubSystemsForm
from ControlSystems_form import ControlSystemsForm
from Manufacturers_form import ManufacturersForm
from InstrumentStatus_form import InstrumentStatusForm
from Instruments_form import InstrumentsForm
from InstrumentLifecycle_form import InstrumentLifecycleForm
from SpareParts_form import SparePartsForm
from SparePartUsage_form import SparePartUsageForm
from AlarmConfiguration_form import AlarmConfigurationForm
from MaintenanceRecords_form import MaintenanceRecordsForm
from FailureRecords_form import FailureRecordsForm


# ----------------------------------------------------------------------
# ---- Design tokens ------------------------------------------------------
# ----------------------------------------------------------------------
COLOR_BG_APP = "#eef1f4"
COLOR_BG_PANEL = "#ffffff"

COLOR_HEADER = "#0a0e13"
COLOR_SIDEBAR = "#10161f"
COLOR_SIDEBAR_HOVER = "#1c2531"
COLOR_SIDEBAR_ACTIVE = "#232f3d"

COLOR_TEXT_LIGHT = "#eceff1"
COLOR_TEXT_MUTED = "#78909c"
COLOR_TEXT_DARK = "#1c2531"

COLOR_AMBER = "#ffa726"
COLOR_AMBER_DARK = "#e08e00"
COLOR_TEAL = "#00bcd4"
COLOR_RED = "#e53935"
COLOR_GREEN = "#43a047"
COLOR_BLUE_GRAY = "#546e7a"

FONT_HEADER = ("Segoe UI", 14, "bold")
FONT_SECTION = ("Segoe UI", 9, "bold")
FONT_NAV = ("Segoe UI", 10, "bold")
FONT_BUTTON = ("Segoe UI", 10, "bold")
FONT_STATUS = ("Segoe UI", 9, "bold")
FONT_TREE_HEADING = ("Segoe UI", 9, "bold")
FONT_TREE_ROW = ("Segoe UI", 9)
FONT_LABEL = ("Segoe UI", 9, "bold")


# ----------------------------------------------------------------------
# Sidebar wiring: (display label, form class, category key)
# ----------------------------------------------------------------------
CATEGORY_MASTER_DATA = "master"
CATEGORY_INSTRUMENTATION = "instrumentation"
CATEGORY_ALARMS = "alarms"

CATEGORY_META = {
    CATEGORY_MASTER_DATA: {"label": "MASTER DATA", "color": COLOR_TEAL},
    CATEGORY_INSTRUMENTATION: {"label": "INSTRUMENTATION", "color": COLOR_AMBER},
    CATEGORY_ALARMS: {"label": "ALARMS & SAFETY", "color": COLOR_RED},
}

SIDEBAR_ITEMS = [
    ("Sites", SitesForm, CATEGORY_MASTER_DATA),
    ("Process Units", ProcessUnitsForm, CATEGORY_MASTER_DATA),
    ("Sub-Systems", SubSystemsForm, CATEGORY_MASTER_DATA),
    ("Control Systems", ControlSystemsForm, CATEGORY_MASTER_DATA),
    ("Manufacturers", ManufacturersForm, CATEGORY_MASTER_DATA),
    ("Instrument Status", InstrumentStatusForm, CATEGORY_INSTRUMENTATION),
    ("Instruments", InstrumentsForm, CATEGORY_INSTRUMENTATION),
    ("Instrument Lifecycle", InstrumentLifecycleForm, CATEGORY_INSTRUMENTATION),
    ("Spare Parts", SparePartsForm, CATEGORY_INSTRUMENTATION),
    ("Spare Part Usage", SparePartUsageForm, CATEGORY_INSTRUMENTATION),
    ("Maintenance Records", MaintenanceRecordsForm, CATEGORY_INSTRUMENTATION),
    ("Failure Records", FailureRecordsForm, CATEGORY_INSTRUMENTATION),
    ("Alarm Configuration", AlarmConfigurationForm, CATEGORY_ALARMS),
]


class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Comprehensive Instrumentation Database")
        self.geometry("1440x880")
        self.minsize(1150, 680)
        self.configure(bg=COLOR_BG_APP)

        self.sidebar_buttons = {}
        self.current_form = None
        self.form_cache = {}
        self._active_label = None
        self._blink_on = True

        self._configure_styles()
        self._build_layout()
        self._tick_clock()
        self._tick_blink()

        if SIDEBAR_ITEMS:
            self._show_form(SIDEBAR_ITEMS[0][0])

    # ------------------------------------------------------------------
    # Global ttk styling
    # ------------------------------------------------------------------
    def _configure_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure(
            "TButton",
            font=FONT_BUTTON,
            padding=(12, 7),
            background=COLOR_BLUE_GRAY,
            foreground="#ffffff",
            borderwidth=0,
            focusthickness=0,
        )
        style.map(
            "TButton",
            background=[("active", "#37474f"), ("disabled", "#b0bec5")],
            foreground=[("disabled", "#eceff1")],
        )

        style.configure("Save.TButton", background=COLOR_GREEN, foreground="#ffffff")
        style.map("Save.TButton", background=[("active", "#2e7d32")])

        style.configure("Delete.TButton", background=COLOR_RED, foreground="#ffffff")
        style.map("Delete.TButton", background=[("active", "#b71c1c")])

        style.configure("New.TButton", background=COLOR_TEAL, foreground="#ffffff")
        style.map("New.TButton", background=[("active", "#00838f")])

        style.configure("Refresh.TButton", background=COLOR_AMBER_DARK, foreground="#ffffff")
        style.map("Refresh.TButton", background=[("active", "#bf6f00")])

        style.configure("TLabel", font=FONT_LABEL, background=COLOR_BG_APP, foreground=COLOR_TEXT_DARK)
        style.configure("TFrame", background=COLOR_BG_APP)
        style.configure(
            "TLabelframe",
            background=COLOR_BG_PANEL,
            bordercolor=COLOR_TEAL,
            relief="solid",
            borderwidth=1,
        )
        style.configure(
            "TLabelframe.Label",
            font=("Segoe UI", 10, "bold"),
            background=COLOR_BG_PANEL,
            foreground=COLOR_TEXT_DARK,
        )

        style.configure(
            "TEntry", padding=5, fieldbackground="#ffffff", bordercolor="#b0bec5"
        )
        style.configure(
            "TCombobox", padding=5, fieldbackground="#ffffff", arrowsize=14
        )

        style.configure("TCheckbutton", font=FONT_LABEL, background=COLOR_BG_PANEL)

        style.configure("TNotebook", background=COLOR_BG_APP, borderwidth=0)
        style.configure(
            "TNotebook.Tab",
            font=("Segoe UI", 9, "bold"),
            padding=(14, 8),
            background="#cfd8dc",
            foreground=COLOR_TEXT_DARK,
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", COLOR_AMBER)],
            foreground=[("selected", "#1c1c1c")],
        )

        style.configure(
            "Treeview",
            font=FONT_TREE_ROW,
            rowheight=26,
            background="#ffffff",
            fieldbackground="#ffffff",
            foreground=COLOR_TEXT_DARK,
            borderwidth=0,
        )
        style.configure(
            "Treeview.Heading",
            font=FONT_TREE_HEADING,
            background=COLOR_SIDEBAR,
            foreground="#ffffff",
            relief="flat",
            padding=(6, 6),
        )
        style.map(
            "Treeview.Heading",
            background=[("active", COLOR_SIDEBAR_HOVER)],
        )
        style.map(
            "Treeview",
            background=[("selected", COLOR_AMBER)],
            foreground=[("selected", "#1c1c1c")],
        )

        style.configure("Vertical.TScrollbar", background=COLOR_BLUE_GRAY, troughcolor="#dde3e8")
        style.configure("Horizontal.TScrollbar", background=COLOR_BLUE_GRAY, troughcolor="#dde3e8")

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------
    def _build_layout(self):
        header = tk.Frame(self, bg=COLOR_HEADER, height=56)
        header.pack(side="top", fill="x")
        header.pack_propagate(False)

        title_frame = tk.Frame(header, bg=COLOR_HEADER)
        title_frame.pack(side="left", padx=18)
        tk.Label(
            title_frame, text="\u2699 COMPREHENSIVE INSTRUMENTATION DATABASE",
            bg=COLOR_HEADER, fg=COLOR_TEXT_LIGHT, font=FONT_HEADER
        ).pack(side="left", pady=12)

        status_frame = tk.Frame(header, bg=COLOR_HEADER)
        status_frame.pack(side="right", padx=18)

        self.clock_label = tk.Label(
            status_frame, text="", bg=COLOR_HEADER, fg=COLOR_TEXT_MUTED,
            font=("Consolas", 10, "bold")
        )
        self.clock_label.pack(side="right", padx=(16, 0))

        pill = tk.Frame(status_frame, bg="#132018", padx=10, pady=5)
        pill.pack(side="right")
        self.blink_dot = tk.Label(pill, text="\u25cf", bg="#132018", fg=COLOR_GREEN, font=("Segoe UI", 11))
        self.blink_dot.pack(side="left")
        tk.Label(
            pill, text=" SYSTEM ONLINE", bg="#132018", fg=COLOR_GREEN, font=FONT_STATUS
        ).pack(side="left")

        body = tk.Frame(self, bg=COLOR_BG_APP)
        body.pack(side="top", fill="both", expand=True)

        self.sidebar = tk.Frame(body, bg=COLOR_SIDEBAR, width=240)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        canvas = tk.Canvas(self.sidebar, bg=COLOR_SIDEBAR, highlightthickness=0)
        scroll_frame = tk.Frame(canvas, bg=COLOR_SIDEBAR)
        vsb = tk.Scrollbar(self.sidebar, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)

        canvas.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        canvas_window = canvas.create_window((0, 0), window=scroll_frame, anchor="nw")

        def _on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def _on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width)

        scroll_frame.bind("<Configure>", _on_frame_configure)
        canvas.bind("<Configure>", _on_canvas_configure)

        self._build_sidebar_sections(scroll_frame)

        self.content = tk.Frame(body, bg=COLOR_BG_APP)
        self.content.pack(side="left", fill="both", expand=True)

        self.status_bar = tk.Label(
            self, text="Ready", bg=COLOR_HEADER, fg=COLOR_TEXT_MUTED,
            font=("Segoe UI", 9, "bold"), anchor="w", padx=14, pady=5
        )
        self.status_bar.pack(side="bottom", fill="x")

    def _build_sidebar_sections(self, parent):
        current_category = None

        for label, form_cls, category in SIDEBAR_ITEMS:
            if category != current_category:
                current_category = category
                meta = CATEGORY_META[category]
                section_label = tk.Frame(parent, bg=COLOR_SIDEBAR)
                section_label.pack(side="top", fill="x", padx=16, pady=(18, 6))
                tk.Label(
                    section_label, text="\u25a0", bg=COLOR_SIDEBAR, fg=meta["color"],
                    font=("Segoe UI", 8)
                ).pack(side="left")
                tk.Label(
                    section_label, text=f" {meta['label']}", bg=COLOR_SIDEBAR,
                    fg=COLOR_TEXT_MUTED, font=FONT_SECTION
                ).pack(side="left")

            meta = CATEGORY_META[category]
            row = tk.Frame(parent, bg=COLOR_SIDEBAR)
            row.pack(side="top", fill="x")

            indicator = tk.Frame(row, bg=COLOR_SIDEBAR, width=4)
            indicator.pack(side="left", fill="y")

            btn = tk.Label(
                row, text=label, bg=COLOR_SIDEBAR, fg=COLOR_TEXT_LIGHT,
                font=FONT_NAV, anchor="w", padx=14, pady=10, cursor="hand2"
            )
            btn.pack(side="left", fill="x", expand=True)

            btn.bind("<Button-1>", lambda e, lbl=label: self._show_form(lbl))
            btn.bind("<Enter>", lambda e, b=btn, lbl=label: self._on_hover(b, lbl, True))
            btn.bind("<Leave>", lambda e, b=btn, lbl=label: self._on_hover(b, lbl, False))
            self.sidebar_buttons[label] = {"row": row, "button": btn, "indicator": indicator,
                                           "color": meta["color"]}

    def _on_hover(self, button, label, entering):
        if self._active_label == label:
            return
        button.configure(bg=COLOR_SIDEBAR_HOVER if entering else COLOR_SIDEBAR)
        self.sidebar_buttons[label]["row"].configure(
            bg=COLOR_SIDEBAR_HOVER if entering else COLOR_SIDEBAR
        )

    # ------------------------------------------------------------------
    # Clock + blinking "online" indicator
    # ------------------------------------------------------------------
    def _tick_clock(self):
        import datetime
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.clock_label.configure(text=now)
        self.after(1000, self._tick_clock)

    def _tick_blink(self):
        self._blink_on = not self._blink_on
        self.blink_dot.configure(fg=COLOR_GREEN if self._blink_on else "#0d3d14")
        self.after(900, self._tick_blink)

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------
    def _show_form(self, label):
        if self._active_label and self._active_label in self.sidebar_buttons:
            prev = self.sidebar_buttons[self._active_label]
            prev["row"].configure(bg=COLOR_SIDEBAR)
            prev["button"].configure(bg=COLOR_SIDEBAR, fg=COLOR_TEXT_LIGHT)
            prev["indicator"].configure(bg=COLOR_SIDEBAR)

        self._active_label = label
        active = self.sidebar_buttons[label]
        active["row"].configure(bg=COLOR_SIDEBAR_ACTIVE)
        active["button"].configure(bg=COLOR_SIDEBAR_ACTIVE, fg=COLOR_AMBER)
        active["indicator"].configure(bg=active["color"])

        if self.current_form is not None:
            self.current_form.pack_forget()

        if label not in self.form_cache:
            form_cls = {lbl: cls for lbl, cls, _ in SIDEBAR_ITEMS}[label]
            self.form_cache[label] = form_cls(self.content)

        self.current_form = self.form_cache[label]
        self.current_form.pack(side="top", fill="both", expand=True)

        self.status_bar.configure(text=f" Viewing: {label}")


if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()
