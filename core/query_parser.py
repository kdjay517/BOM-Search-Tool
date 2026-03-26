class QueryParser:

    def parse(self, query):

        tokens = query.split()

        filters = {}
        keyword = None

        for token in tokens:

            if ":" in token:

                key, value = token.split(":", 1)

                filters[key.lower()] = value.lower()

            else:

                keyword = token.lower()

        return keyword, filters