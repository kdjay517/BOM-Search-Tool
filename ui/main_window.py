import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import os

from database.db_manager import DBManager
from core.indexer import BOMIndexer
from core.search_engine import SearchEngine
from ui.results_table import ResultTable
from utils.excel_handler import ExcelHandler


class MainWindow:

    def __init__(self):

        self.root = tk.Tk()
        self.root.title("BOM Search Tool")
        self.root.geometry("1400x750")

        # core modules
        self.db = DBManager()
        self.indexer = BOMIndexer(self.db)
        self.search_engine = SearchEngine(self.db)
        self.excel = ExcelHandler()

        # runtime data
        self.current_rows = []
        self.loaded_files = []
        self.file_vars = {}

        # build UI
        self.build_ui()

        # load previously indexed BOM files
        self.load_existing_files()

    # ----------------------------
    # UI Layout
    # ----------------------------
    def build_ui(self):

        top = tk.Frame(self.root)
        top.pack(fill="x", padx=5, pady=5)

        # -------- LOAD BUTTON --------
        load_btn = tk.Button(
            top,
            text="📂 Load BOM Files",
            command=self.load_files
        )
        load_btn.pack(side="left")

        # -------- EXPORT BUTTON --------
        export_btn = tk.Button(
            top,
            text="📤 Export Results",
            command=self.export_results
        )
        export_btn.pack(side="left", padx=5)

        # -------- SPACER --------
        spacer = tk.Frame(top)
        spacer.pack(side="left", expand=True)

        # -------- SEARCH FRAME --------
        search_frame = tk.Frame(top)
        search_frame.pack(side="right", padx=10)

        search_icon = tk.Label(search_frame, text="🔍")
        search_icon.pack(side="left")

        self.search_entry = tk.Entry(
            search_frame,
            width=35,
            fg="gray"
        )
        self.search_entry.pack(side="left")

        # placeholder text
        self.search_entry.insert(0, "Enter keyword")

        def clear_placeholder(event):
            if self.search_entry.get() == "Enter keyword":
                self.search_entry.delete(0, tk.END)
                self.search_entry.config(fg="black")

        def restore_placeholder(event):
            if not self.search_entry.get():
                self.search_entry.insert(0, "Enter keyword")
                self.search_entry.config(fg="gray")

        self.search_entry.bind("<FocusIn>", clear_placeholder)
        self.search_entry.bind("<FocusOut>", restore_placeholder)

        self.search_entry.bind("<KeyRelease>", self.search)

        # -------- BOM FILE CONTAINER --------
        files_frame = tk.LabelFrame(self.root, text="Loaded BOM Files")
        files_frame.pack(fill="x", padx=10, pady=5)

        self.files_container = tk.Frame(files_frame)
        self.files_container.pack(fill="x")

        # -------- RESULTS TABLE --------
        self.table = ResultTable(self.root, self.open_excel_row)

    # ----------------------------
    # Load BOM files from disk
    # ----------------------------
    def load_files(self):

        files = filedialog.askopenfilenames(
            title="Select BOM Files",
            filetypes=[("Excel Files", "*.xlsx *.xls")]
        )

        if not files:
            return

        valid_files = []

        for file in files:

            if file in self.loaded_files:
                continue

            try:

                self.indexer.index_files([file])

                valid_files.append(file)

                self.db.add_loaded_file(file)

            except ValueError as e:

                messagebox.showerror(
                    "Invalid BOM",
                    str(e)
                )

        if not valid_files:
            return

        self.loaded_files.extend(valid_files)

        self.refresh_file_list()

    # ----------------------------
    # Load previous BOM files
    # ----------------------------
    def load_existing_files(self):

        files = self.db.get_loaded_files()

        if not files:
            return

        self.loaded_files = files

        try:
            self.indexer.index_files(files)
        except:
            pass

        self.refresh_file_list()

    # ----------------------------
    # Refresh checkbox list
    # ----------------------------
    def refresh_file_list(self):

        for widget in self.files_container.winfo_children():
            widget.destroy()

        self.file_vars = {}

        for file in self.loaded_files:

            name = os.path.basename(file)

            var = tk.BooleanVar(value=True)

            chk = tk.Checkbutton(
                self.files_container,
                text=name,
                variable=var
            )

            chk.pack(anchor="w")

            self.file_vars[file] = var

    # ----------------------------
    # Search BOM data
    # ----------------------------
    def search(self, event=None):

        query = self.search_entry.get()

        if query == "Enter keyword":
            query = ""

        rows = self.search_engine.search(query)

        selected_files = [
            file for file, var in self.file_vars.items()
            if var.get()
        ]

        if selected_files:
            rows = [r for r in rows if r[0] in selected_files]

        self.current_rows = rows

        self.table.update(rows)

    # ----------------------------
    # Export results
    # ----------------------------
    def export_results(self):

        if not self.current_rows:
            return

        df = pd.DataFrame(self.current_rows)

        path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel File", "*.xlsx")]
        )

        if not path:
            return

        df.to_excel(path, index=False)

    # ----------------------------
    # Open Excel file
    # ----------------------------
    def open_excel_row(self, file_path):

        self.excel.open_excel(file_path)

    # ----------------------------
    # Run app
    # ----------------------------
    def run(self):

        self.root.mainloop()