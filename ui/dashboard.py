class Dashboard:

    def generate(self, df):

        total = len(df)

        pending = len(df[df["Remaining Qty (Auto)"] > 0])

        closed = len(df[df["Status"] == "Closed"])

        return {
            "total_parts": total,
            "pending_procurement": pending,
            "closed_orders": closed
        }
