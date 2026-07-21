"""
TripInstruments_form.py

CRUD form for the TripInstruments table (junction table linking Instruments
to TripsInterlocks, with voting logic - e.g. 2oo3 - for each instrument's
role in a given trip).

    CREATE TABLE TripInstruments (
        TripInstrumentID INT PRIMARY KEY IDENTITY(1,1),
        TripID INT NOT NULL,
        InstrumentID INT NOT NULL,
        VotingLogic NVARCHAR(20),
        IsPrimary BIT DEFAULT 1,
        FOREIGN KEY (TripID) REFERENCES TripsInterlocks(TripID),
        FOREIGN KEY (InstrumentID) REFERENCES Instruments(InstrumentID)
    );

Follows the same conventions as the other forms in this project:
    - get_connection() from db_connection (pyodbc / ODBC Driver 17 / Windows Auth)
    - FK comboboxes:
        TripID       -> TripsInterlocks (TripTag - TripDescription), required
        InstrumentID -> Instruments (TagNumber - Description), required
    - VotingLogic is a free-editable combobox with common voting patterns
      (1oo1, 1oo2, 2oo2, 2oo3, etc.) as suggestions, not a locked list, since
      the schema comment shows examples rather than an enumerated set
    - IsPrimary defaults to checked, matching DEFAULT 1 in the DDL
    - pyodbc.IntegrityError caught separately for meaningful constraint messages
    - Dynamic FK-dependency check on delete using sys.foreign_keys
    - Column-scoped search / filter panel with live keyword filtering
"""

import tkinter as tk
from tkinter import ttk, messagebox

import pyodbc

from db_connection import get_connection


VOTING_LOGIC_SUGGESTIONS = ["1oo1", "1oo2", "2oo2", "2oo3", "1oo3", "2oo4"]


class TripInstrumentsForm(ttk.Frame):
    TABLE_NAME = "TripInstruments"

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.selected_id = None
        self.trip_lookup = {}         # display string -> TripID
        self.instrument_lookup = {}   # display string -> InstrumentID

        self._build_ui()
        self._load_trip_lookup()
        self._load_instrument_lookup()
        self.refresh_data()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------
    def _build_ui(self):
        # ---------------- Filter panel ----------------
        filter_frame = ttk.LabelFrame(self, text="Search / Filter")
        filter_frame.pack(side="top", fill="x", padx=8, pady=(8, 4))

        ttk.Label(filter_frame, text="Trip / Interlock:").grid(row=0, column=0, sticky="w", padx=5, pady=4)
        self.trip_filter_var = tk.StringVar()
        self.trip_filter_combo = ttk.Combobox(
            filter_frame, textvariable=self.trip_filter_var, state="readonly", width=34
        )
        self.trip_filter_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=4)
        self.trip_filter_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_data())

        ttk.Label(filter_frame, text="Instrument:").grid(row=0, column=2, sticky="w", padx=5, pady=4)
        self.instrument_filter_var = tk.StringVar()
        self.instrument_filter_combo = ttk.Combobox(
            filter_frame, textvariable=self.instrument_filter_var, state="readonly", width=32
        )
        self.instrument_filter_combo.grid(row=0, column=3, sticky="ew", padx=5, pady=4)
        self.instrument_filter_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_data())

        btn_frame = ttk.Frame(filter_frame)
        btn_frame.grid(row=1, column=0, columnspan=4, sticky="w", padx=5, pady=(0, 4))
        ttk.Button(btn_frame, text="Apply Filter", command=self.refresh_data).pack(side="left", padx=3)
        ttk.Button(btn_frame, text="Clear Filter", command=self._clear_filter).pack(side="left", padx=3)

        for col in range(4):
            filter_frame.columnconfigure(col, weight=1)

        # ---------------- Treeview ----------------
        tree_frame = ttk.Frame(self)
        tree_frame.pack(side="top", fill="both", expand=True, padx=8, pady=4)

        columns = ("TripInstrumentID", "Trip", "Instrument", "VotingLogic", "IsPrimary")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=10)
        headings = {
            "TripInstrumentID": "ID", "Trip": "Trip / Interlock", "Instrument": "Instrument",
            "VotingLogic": "Voting Logic", "IsPrimary": "Primary",
        }
        widths = {
            "TripInstrumentID": 50, "Trip": 220, "Instrument": 220,
            "VotingLogic": 100, "IsPrimary": 70,
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
        panel = ttk.LabelFrame(self, text="Trip Instrument Details")
        panel.pack(side="top", fill="x", padx=8, pady=4)
        for col in range(4):
            panel.columnconfigure(col, weight=1)

        # TripInstrumentID (disabled, identity)
        ttk.Label(panel, text="Trip Instrument ID:").grid(row=0, column=0, sticky="w", padx=5, pady=4)
        self.id_var = tk.StringVar()
        ttk.Entry(panel, textvariable=self.id_var, width=20, state="disabled").grid(
            row=0, column=1, sticky="ew", padx=5, pady=4
        )

        # Trip / Interlock (FK combobox, required)
        ttk.Label(panel, text="Trip / Interlock *:").grid(row=0, column=2, sticky="w", padx=5, pady=4)
        self.trip_var = tk.StringVar()
        self.trip_combo = ttk.Combobox(panel, textvariable=self.trip_var, state="readonly", width=32)
        self.trip_combo.grid(row=0, column=3, sticky="ew", padx=5, pady=4)

        # Instrument (FK combobox, required)
        ttk.Label(panel, text="Instrument *:").grid(row=1, column=0, sticky="w", padx=5, pady=4)
        self.instrument_var = tk.StringVar()
        self.instrument_combo = ttk.Combobox(
            panel, textvariable=self.instrument_var, state="readonly", width=28
        )
        self.instrument_combo.grid(row=1, column=1, sticky="ew", padx=5, pady=4)

        # VotingLogic (free-editable combo with suggestions)
        ttk.Label(panel, text="Voting Logic:").grid(row=1, column=2, sticky="w", padx=5, pady=4)
        self.voting_logic_var = tk.StringVar()
        ttk.Combobox(
            panel, textvariable=self.voting_logic_var, width=26, values=VOTING_LOGIC_SUGGESTIONS
        ).grid(row=1, column=3, sticky="ew", padx=5, pady=4)

        # IsPrimary (bit, default checked)
        ttk.Label(panel, text="Is Primary:").grid(row=2, column=0, sticky="w", padx=5, pady=4)
        self.is_primary_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(panel, variable=self.is_primary_var).grid(
            row=2, column=1, sticky="w", padx=5, pady=4
        )

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
        ttk.Button(
            action_frame, text="Reload Lookups",
            command=lambda: (self._load_trip_lookup(), self._load_instrument_lookup())
        ).pack(side="left", padx=3)

    def _clear_filter(self):
        self.trip_filter_var.set("(All)" if "(All)" in self.trip_filter_combo["values"] else "")
        self.instrument_filter_var.set(
            "(All)" if "(All)" in self.instrument_filter_combo["values"] else ""
        )
        self.refresh_data()

    # ------------------------------------------------------------------
    # Trip / Interlock FK lookup
    # ------------------------------------------------------------------
    def _load_trip_lookup(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT TripID, TripTag, TripDescription
                FROM TripsInterlocks
                ORDER BY TripTag
                """
            )
            rows = cursor.fetchall()
            conn.close()

            self.trip_lookup = {}
            display_values = []
            for trip_id, trip_tag, trip_description in rows:
                display = f"{trip_tag} - {trip_description}" if trip_description else trip_tag
                self.trip_lookup[display] = trip_id
                display_values.append(display)

            self.trip_combo["values"] = display_values
            self.trip_filter_combo["values"] = ["(All)"] + display_values
            if not self.trip_filter_var.get():
                self.trip_filter_var.set("(All)")

        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to load Trips/Interlocks lookup:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error while loading Trips/Interlocks:\n{e}")

    def _trip_display_for_id(self, trip_id):
        for display, tid in self.trip_lookup.items():
            if tid == trip_id:
                return display
        return f"[ID {trip_id}]"

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
                SELECT ti.TripInstrumentID, t.TripTag, i.TagNumber, i.Description,
                       ti.VotingLogic, ti.IsPrimary
                FROM TripInstruments ti
                LEFT JOIN TripsInterlocks t ON ti.TripID = t.TripID
                LEFT JOIN Instruments i ON ti.InstrumentID = i.InstrumentID
                WHERE 1=1
            """
            params = []

            trip_display = self.trip_filter_var.get()
            if trip_display and trip_display != "(All)":
                trip_id = self.trip_lookup.get(trip_display)
                if trip_id is not None:
                    query += " AND ti.TripID = ?"
                    params.append(trip_id)

            instrument_display = self.instrument_filter_var.get()
            if instrument_display and instrument_display != "(All)":
                instrument_id = self.instrument_lookup.get(instrument_display)
                if instrument_id is not None:
                    query += " AND ti.InstrumentID = ?"
                    params.append(instrument_id)

            query += " ORDER BY t.TripTag, i.TagNumber"

            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()

            for item in self.tree.get_children():
                self.tree.delete(item)

            for row in rows:
                (trip_instrument_id, trip_tag, tag_number, description,
                 voting_logic, is_primary) = row
                instrument_label = f"{tag_number} - {description}" if description else (tag_number or "")
                self.tree.insert(
                    "", "end", iid=str(trip_instrument_id),
                    values=(
                        trip_instrument_id, trip_tag or "", instrument_label,
                        voting_logic or "", "Yes" if is_primary else "No",
                    )
                )

        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to load Trip Instruments data:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error while loading data:\n{e}")

    # ------------------------------------------------------------------
    # Selection / form population
    # ------------------------------------------------------------------
    def _on_select(self, event):
        selection = self.tree.selection()
        if not selection:
            return

        trip_instrument_id = int(selection[0])
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT TripInstrumentID, TripID, InstrumentID, VotingLogic, IsPrimary
                FROM TripInstruments
                WHERE TripInstrumentID = ?
                """,
                (trip_instrument_id,)
            )
            row = cursor.fetchone()
            conn.close()

            if not row:
                return

            (tiid, trip_id, instrument_id, voting_logic, is_primary) = row

            self.selected_id = tiid
            self.id_var.set(str(tiid))
            self.trip_var.set(self._trip_display_for_id(trip_id))
            self.instrument_var.set(self._instrument_display_for_id(instrument_id))
            self.voting_logic_var.set(voting_logic or "")
            self.is_primary_var.set(bool(is_primary))

        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to load Trip Instrument record:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error while loading record:\n{e}")

    def _new_record(self):
        self.selected_id = None
        self.id_var.set("")
        self.trip_var.set("")
        self.instrument_var.set("")
        self.voting_logic_var.set("")
        self.is_primary_var.set(True)
        self.tree.selection_remove(self.tree.selection())

    # ------------------------------------------------------------------
    # Save (Insert / Update)
    # ------------------------------------------------------------------
    def _save_record(self):
        trip_display = self.trip_var.get().strip()
        instrument_display = self.instrument_var.get().strip()

        if not trip_display:
            messagebox.showwarning("Validation", "Please select a Trip / Interlock.")
            return
        if not instrument_display:
            messagebox.showwarning("Validation", "Please select an Instrument.")
            return

        trip_id = self.trip_lookup.get(trip_display)
        if trip_id is None:
            messagebox.showwarning("Validation", "Please select a valid Trip / Interlock from the list.")
            return

        instrument_id = self.instrument_lookup.get(instrument_display)
        if instrument_id is None:
            messagebox.showwarning("Validation", "Please select a valid Instrument from the list.")
            return

        voting_logic = self.voting_logic_var.get().strip() or None
        is_primary = self.is_primary_var.get()

        try:
            conn = get_connection()
            cursor = conn.cursor()

            if self.selected_id:
                cursor.execute(
                    """
                    UPDATE TripInstruments
                    SET TripID = ?, InstrumentID = ?, VotingLogic = ?, IsPrimary = ?
                    WHERE TripInstrumentID = ?
                    """,
                    (trip_id, instrument_id, voting_logic, is_primary, self.selected_id)
                )
                conn.commit()
                messagebox.showinfo("Success", "Trip Instrument updated successfully.")
            else:
                cursor.execute(
                    """
                    INSERT INTO TripInstruments (TripID, InstrumentID, VotingLogic, IsPrimary)
                    VALUES (?, ?, ?, ?)
                    """,
                    (trip_id, instrument_id, voting_logic, is_primary)
                )
                conn.commit()
                messagebox.showinfo("Success", "Trip Instrument added successfully.")

            conn.close()
            self.refresh_data()
            self._new_record()

        except pyodbc.IntegrityError as e:
            messagebox.showerror(
                "Integrity Error",
                f"Save failed. This likely indicates an invalid Trip/Interlock or "
                f"Instrument reference:\n{e}"
            )
        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to save Trip Instrument:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error while saving:\n{e}")

    # ------------------------------------------------------------------
    # Delete (with dynamic FK dependency check)
    # ------------------------------------------------------------------
    def _get_dependent_records(self, conn, trip_instrument_id):
        """
        Dynamically discover every table with a FK referencing TripInstruments,
        then count rows that reference this TripInstrumentID. Nothing
        references it today, but this keeps the form correct if that changes.
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
                    (trip_instrument_id,)
                )
                count = count_cursor.fetchone()[0]
                if count > 0:
                    dependents.append((child_table, count))
            except pyodbc.Error:
                continue

        return dependents

    def _delete_record(self):
        if not self.selected_id:
            messagebox.showwarning("No Selection", "Please select a Trip Instrument to delete.")
            return

        try:
            conn = get_connection()
            dependents = self._get_dependent_records(conn, self.selected_id)

            if dependents:
                detail = "\n".join(f"  - {table}: {count} record(s)" for table, count in dependents)
                proceed = messagebox.askyesno(
                    "Trip Instrument In Use",
                    f"This Trip Instrument is referenced by other records:\n\n{detail}\n\n"
                    "Deleting it may fail or orphan related data depending on your "
                    "database's FK constraints.\n\nDo you still want to attempt deletion?"
                )
                if not proceed:
                    conn.close()
                    return
            else:
                confirm = messagebox.askyesno(
                    "Confirm Delete",
                    f"Delete this Trip Instrument (ID {self.selected_id})?"
                )
                if not confirm:
                    conn.close()
                    return

            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM TripInstruments WHERE TripInstrumentID = ?", (self.selected_id,)
            )
            conn.commit()
            conn.close()

            messagebox.showinfo("Deleted", "Trip Instrument deleted successfully.")
            self.refresh_data()
            self._new_record()

        except pyodbc.IntegrityError as e:
            messagebox.showerror(
                "Integrity Error",
                f"Cannot delete this Trip Instrument because other records depend on it:\n{e}"
            )
        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Failed to delete Trip Instrument:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error while deleting:\n{e}")
