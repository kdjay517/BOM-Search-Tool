from datetime import datetime
import pandas as pd


class ProcurementAnalyzer:

    def parse_date(self, value):
        """
        Safely convert different Excel date formats into datetime
        """

        if not value:
            return None

        try:

            # if Excel serial number
            if isinstance(value, (int, float)):
                return pd.to_datetime(value, unit="D", origin="1899-12-30")

            # normal date string
            return pd.to_datetime(value, errors="coerce")

        except:
            return None

    def analyze(self, row):

        try:

            qty_procure = float(row[9] or 0)
            received_qty = float(row[20] or 0)

            est_date = self.parse_date(row[19])

            invoice = row[21]

            today = datetime.today()

            # Delivery delay
            if est_date and est_date < today and received_qty == 0:
                return "delay"

            # Partial delivery
            if received_qty > 0 and received_qty < qty_procure:
                return "partial"

            # Invoice missing
            if received_qty > 0 and not invoice:
                return "invoice_missing"

        except:
            pass

        return "normal"