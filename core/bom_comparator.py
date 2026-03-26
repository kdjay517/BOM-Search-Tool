import pandas as pd


class BOMComparator:

    def load_bom(self, file):

        xls = pd.ExcelFile(file)

        for sheet in xls.sheet_names:

            if "bom" in sheet.lower():
                return pd.read_excel(file, sheet_name=sheet)

    def compare(self, file1, file2):

        bom1 = self.load_bom(file1)
        bom2 = self.load_bom(file2)

        key = "Assembly Part No"

        set1 = set(bom1[key])
        set2 = set(bom2[key])

        added = set2 - set1
        removed = set1 - set2

        return {
            "added": bom2[bom2[key].isin(added)],
            "removed": bom1[bom1[key].isin(removed)]
        }