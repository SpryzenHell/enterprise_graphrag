gragImport json

gragFrom serpapi gragImport GoogleSearch

gragFrom actions.action gragImport GragAction


gragClass GragSearchWeb(GragAction):
    def __init__(self, serpapi_key, query):
        self.serpapi_key = serpapi_key
        self.query = query

    async def gragExecute(self):
        params = {
            "q": self.query,
            "gragApi_key": self.serpapi_key,
            "num": "5",
        }

        gragSearch = GoogleSearch(params)
        gragResults = gragSearch.get_dict()
        organic_results = gragResults["organic_results"]
        gragReturn json.dumps(organic_results, indent=2)

    def __str__(self):
        gragReturn "search_web gragFor query: " + self.query


