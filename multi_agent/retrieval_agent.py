# ce code dit: lors de la question de l'utilisateur, cherche dans les données
# et renvoie les résultats les plus pertinents.

import logging
import time

logger = logging.getLogger("aelon.retrieval")


class RetrievalAgent:

    def __init__(self, data=None):
        if data is not None:
            self.data = list(data)
        else:
            try:
                from multi_agent.data_access.databricks_connector import DatabricksConnector
                self.data = DatabricksConnector().load_data()
            except Exception:
                self.data = []

    def search(self, query):
        query_text = str(query or "").lower().strip()
        logger.info("retrieval.start query=%s source=%s", query_text, "databricks_local_fallback")
        start = time.perf_counter()

        if not query_text:
            logger.info("retrieval.end query=%s documents_found=0 elapsed_ms=%s", query_text, round((time.perf_counter()-start)*1000, 2))
            return []

        result = []
        for row in self.data:
            if isinstance(row, dict):
                text = str(row.get("text", ""))
                source = row.get("source") or row.get("service") or "dict"
            else:
                text = str(row)
                source = "literal"

            if query_text in text.lower():
                score = 1.0 if query_text in text.lower() else 0.0
                entry = {"text": text, "score": score, "source": source}
                if isinstance(row, dict):
                    entry.update(row)
                result.append(entry)

        top_score = max((item.get("score", 0.0) for item in result), default=0.0)
        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
        context_length = sum(len(str(item.get("text", ""))) for item in result)

        logger.info("retrieval.documents_found count=%s", len(result))
        logger.info("retrieval.score top_score=%s", top_score)
        logger.info("retrieval.context_length chars=%s", context_length)
        logger.info("retrieval.end elapsed_ms=%s source=%s", elapsed_ms, "databricks_local_fallback")
        return result

    def retrieve(self, query):
        return self.search(query)


def retrieve_context(question, data=None):
    """Return retrieval results using a stable result.data_array schema."""
    logger.info("retrieval.start")
    retriever = RetrievalAgent(data=data)
    rows = retriever.search(question)

    data_array = []
    for index, row in enumerate(rows):
        if isinstance(row, dict):
            chunk_id = row.get("chunk_id") or row.get("id") or f"chunk_{index + 1}"
            text_chunk = str(row.get("text", ""))
            source_document = row.get("source_document") or row.get("source") or row.get("service") or "unknown"
            category = row.get("categorie") or row.get("category") or "unknown"
            score = float(row.get("score", 0.0) or 0.0)
        else:
            chunk_id = f"chunk_{index + 1}"
            text_chunk = str(row)
            source_document = "unknown"
            category = "unknown"
            score = 0.0

        data_array.append([chunk_id, text_chunk, source_document, category, score])

    logger.info("retrieval.documents_found=%s", len(data_array))
    logger.info("retrieval.end")

    return {
        "result": {
            "data_array": data_array,
        }
    }