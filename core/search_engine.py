from core.query_parser import QueryParser


class SearchEngine:

    def __init__(self, db):

        self.db = db
        self.parser = QueryParser()

    def search(self, query):

        keyword, filters = self.parser.parse(query)

        rows = self.db.search(keyword if keyword else "")

        # no filters → return all
        if not filters:
            return rows

        results = []

        for r in rows:

            (
                file,
                sheet,
                row_index,
                assembly,
                model,
                manufacturer,
                part,
                spec,
                qty_rig,
                rigs,
                qty_procure,
                price,
                quote_lead,
                nego_lead,
                supplier
            ) = r

            # supplier filter
            if "supplier" in filters:
                if filters["supplier"] not in str(supplier).lower():
                    continue

            # manufacturer filter
            if "manufacturer" in filters:
                if filters["manufacturer"] not in str(manufacturer).lower():
                    continue

            results.append(r)

        return results