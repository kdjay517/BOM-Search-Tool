import pandas as pd
from datetime import datetime


class AlertEngine:

    def remaining_items(self, df):

        if "Remaining Qty (Auto)" in df.columns:
            return df[df["Remaining Qty (Auto)"] > 0]

    def delayed_items(self, df):

        if "Estimated receive Date (Auto)" not in df.columns:
            return []

        today = datetime.today()

        delayed = []

        for _, row in df.iterrows():

            due = row["Estimated receive Date (Auto)"]

            if pd.notna(due) and today > due:
                delayed.append(row)

        return delayed
