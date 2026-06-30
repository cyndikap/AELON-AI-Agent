from multi_agent.data_access.databricks_connector import DatabricksConnector


class RetrievalAgent:

    def __init__(self, data=None):
        if data is not None:
            self.data = data
        else:
            try:
                self.data = DatabricksConnector().load_data()
            except Exception:
                self.data = []

    def search(self, query):
        result = []
        query_text = str(query or "").lower().strip()

        for row in self.data:
            if isinstance(row, dict):
                text = str(row.get("text", ""))
            else:
                text = str(row)

            if query_text and query_text in text.lower():
                result.append(row)

        return result

    def retrieve(self, query):
        return self.search(query)