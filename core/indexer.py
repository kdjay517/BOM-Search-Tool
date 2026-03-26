import pandas as pd
import os


class BOMIndexer:

    def __init__(self, db):
        self.db = db

    # normalize column names
    def normalize(self, text):
        return str(text).lower().replace("\n", " ").replace(".", "").replace("/", "").strip()

    # find header row automatically
    def find_header_row(self, file, sheet):

        preview = pd.read_excel(file, sheet_name=sheet, header=None, nrows=20)

        for i, row in preview.iterrows():

            values = [self.normalize(v) for v in row]

            joined = " ".join(values)

            if "part" in joined and "manufacturer" in joined:
                return i

        return None

    # detect BOM columns dynamically
    def detect_columns(self, columns):

        mapping = {}

        for col in columns:

            name = self.normalize(col)

            if "assembly" in name:
                mapping["assembly"] = col

            elif "model" in name:
                mapping["model"] = col

            elif "manufact" in name:
                mapping["manufacturer"] = col

            elif "part" in name and "model" not in name:
                mapping["part"] = col

            elif "spec" in name:
                mapping["spec"] = col

            elif "#rig" in name or "number of rigs" in name:
                mapping["rigs"] = col

            elif "qty" in name and "rig" in name:
                mapping["qty_rig"] = col

            elif "procure" in name:
                mapping["qty_procure"] = col

            elif "price" in name:
                mapping["price"] = col

            elif "quotation lead" in name:
                mapping["quote_lead"] = col

            elif "negotiated lead" in name:
                mapping["nego_lead"] = col

            elif "supplier" in name or "vendor" in name:
                mapping["supplier"] = col

            elif "pr date" in name:
                mapping["pr_date"] = col

            elif "pr no" in name:
                mapping["pr_no"] = col

            elif "release" in name and "po" in name:
                mapping["po_release_date"] = col

            elif "po no" in name:
                mapping["po_no"] = col

            elif "po date" in name:
                mapping["po_date"] = col

            elif "estimated" in name and "receive" in name:
                mapping["estimated_receive"] = col

            elif "received" in name and "qty" in name:
                mapping["received_qty"] = col

            elif "invoice" in name:
                mapping["invoice_no"] = col

            elif "status" in name:
                mapping["status"] = col

        return mapping

    # detect BOM template type
    def detect_template(self, mapping):

        if "assembly" in mapping and "manufacturer" in mapping:
            return "standard_bom"

        if "supplier" in mapping and "price" in mapping:
            return "supplier_bom"

        if "part" in mapping and "spec" in mapping:
            return "minimal_bom"

        return "unknown"

    # safe getter
    def get_value(self, row, column):

        if not column:
            return ""

        try:

            value = row[column]

            if pd.isna(value):
                return ""

            return str(value)

        except:
            return ""

    # index BOM files
    def index_files(self, files):

        for file in files:

            file_name = os.path.basename(file)

            print("Processing:", file_name)

            # -------- DELETE OLD RECORDS --------
            # prevents duplicates when reloading same BOM
            self.db.delete_file_records(file)

            xls = pd.ExcelFile(file)

            bom_found = False

            for sheet in xls.sheet_names:

                header_row = self.find_header_row(file, sheet)

                if header_row is None:
                    continue

                df = pd.read_excel(file, sheet_name=sheet, header=header_row)

                mapping = self.detect_columns(df.columns)

                print("Sheet:", sheet)
                print("Header row:", header_row)
                print("Detected columns:", mapping)

                template = self.detect_template(mapping)

                print("Detected BOM Template:", template)

                if template != "unknown":
                    bom_found = True

                if template == "unknown":
                    continue

                if "part" not in mapping:
                    continue

                for idx, row in df.iterrows():

                    record = (

                        file,
                        idx + header_row + 2,

                        self.get_value(row, mapping.get("assembly")),
                        self.get_value(row, mapping.get("model")),
                        self.get_value(row, mapping.get("manufacturer")),
                        self.get_value(row, mapping.get("part")),
                        self.get_value(row, mapping.get("spec")),

                        self.get_value(row, mapping.get("qty_rig")),
                        self.get_value(row, mapping.get("rigs")),
                        self.get_value(row, mapping.get("qty_procure")),

                        self.get_value(row, mapping.get("price")),
                        self.get_value(row, mapping.get("quote_lead")),
                        self.get_value(row, mapping.get("nego_lead")),

                        self.get_value(row, mapping.get("supplier")),

                        self.get_value(row, mapping.get("pr_date")),
                        self.get_value(row, mapping.get("pr_no")),

                        self.get_value(row, mapping.get("po_release_date")),
                        self.get_value(row, mapping.get("po_no")),
                        self.get_value(row, mapping.get("po_date")),

                        self.get_value(row, mapping.get("estimated_receive")),
                        self.get_value(row, mapping.get("received_qty")),
                        self.get_value(row, mapping.get("invoice_no")),
                        self.get_value(row, mapping.get("status"))

                    )

                    self.db.insert(record)

            if not bom_found:
                raise ValueError(f"{file_name} is not a valid BOM file")

        self.db.commit()

        print("Indexing complete")