import os


class ExcelHandler:

    def open_excel(self, file):

        if os.name == "nt":
            os.startfile(file)
