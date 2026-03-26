from tkinter import ttk
import os

from core.procurement_analyzer import ProcurementAnalyzer


class ResultTable:

    def __init__(self, parent, open_callback):

        self.open_callback = open_callback
        self.analyzer = ProcurementAnalyzer()

        columns = [

            "File", "Row",
            "Assembly", "Model", "Manufacturer",
            "Part", "Specification",
            "Qty/Rig", "No.Rigs", "Qty Procure",
            "Unit Price", "Quote Lead", "Negotiated Lead",
            "Supplier",
            "PR Date", "PR No",
            "PO Release Date", "PO No", "PO Date",
            "Estimated Receive Date", "Received Qty",
            "Invoice No", "Status"

        ]

        # ---------- container frame ----------
        container = ttk.Frame(parent)
        container.pack(fill="both", expand=True)

        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)

        # ---------- treeview ----------
        self.table = ttk.Treeview(
            container,
            columns=columns,
            show="headings"
        )

        # ---------- scrollbars ----------
        v_scroll = ttk.Scrollbar(
            container,
            orient="vertical",
            command=self.table.yview
        )

        h_scroll = ttk.Scrollbar(
            container,
            orient="horizontal",
            command=self.table.xview
        )

        self.table.configure(
            yscrollcommand=v_scroll.set,
            xscrollcommand=h_scroll.set
        )

        # ---------- layout using grid ----------
        self.table.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")

        # ---------- configure columns ----------
        for col in columns:

            self.table.heading(col, text=col)

            self.table.column(
                col,
                width=140,
                stretch=False   # prevents auto stretching
            )

        # ---------- row color tags ----------
        self.table.tag_configure(
            "delay",
            background="#ffb3b3"
        )

        self.table.tag_configure(
            "partial",
            background="#ffd699"
        )

        self.table.tag_configure(
            "invoice",
            background="#fff2b3"
        )

        self.table.bind("<Double-1>", self.double_click)

    # -------------------------------------------------
    # Update table rows
    # -------------------------------------------------
    def update(self, rows):

        self.table.delete(*self.table.get_children())

        for r in rows:

            status = self.analyzer.analyze(r)

            tag = ""

            if status == "delay":
                tag = "delay"

            elif status == "partial":
                tag = "partial"

            elif status == "invoice_missing":
                tag = "invoice"

            self.table.insert(
                "",
                "end",
                values=r,
                tags=(tag,)
            )

    # -------------------------------------------------
    # Double click open Excel
    # -------------------------------------------------
    def double_click(self, event):

        item = self.table.selection()

        if not item:
            return

        item_id = item[0]

        file_path = self.table.set(item_id, "File")

        self.open_callback(file_path)