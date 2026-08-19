import logging
import os
import time

from dotenv import load_dotenv

logger = logging.getLogger("aelon.retrieval")

load_dotenv()

EMBEDDING_MODEL = os.getenv("DATABRICKS_EMBEDDING_MODEL", "databricks-gte-large-en")
VECTOR_SEARCH_ENDPOINT = os.getenv("DATABRICKS_VECTOR_SEARCH_ENDPOINT", "aelon_vs_endpoint")
VECTOR_SEARCH_INDEX = os.getenv(
    "DATABRICKS_VECTOR_SEARCH_INDEX",
    "fr_raise.rag_pipeline.gold_embeddings_index",
)


class RetrievalAgent:

    def __init__(self):
        self._deploy_client = None
        self._index = None

    def _get_clients(self):
        if self._deploy_client is not None and self._index is not None:
            return self._deploy_client, self._index

        import mlflow.deployments
        from databricks.vector_search.client import VectorSearchClient

        deploy_client = mlflow.deployments.get_deploy_client("databricks")
        vs_client = VectorSearchClient(
            workspace_url=os.getenv("DATABRICKS_HOST"),
            personal_access_token=os.getenv("DATABRICKS_TOKEN"),
        )
        index = vs_client.get_index(
            endpoint_name=VECTOR_SEARCH_ENDPOINT,
            index_name=VECTOR_SEARCH_INDEX,
        )

        self._deploy_client = deploy_client
        self._index = index
        return deploy_client, index

    def retrieve_context(self, question: str, num_results: int = 5):
        logger.info("retrieval.start")
        start = time.perf_counter()

        question_text = str(question or "").strip()
        if not question_text:
            logger.info("retrieval.documents_found=0")
            logger.info("retrieval.end")
            return {"result": {"data_array": []}}

        deploy_client, index = self._get_clients()

        response = deploy_client.predict(
            endpoint=EMBEDDING_MODEL,
            inputs={"input": [question_text]},
        )
        question_vector = response.data[0]["embedding"]

        results = index.similarity_search(
            query_vector=question_vector,
            columns=["chunk_id", "texte_chunk", "source_document", "categorie"],
            num_results=num_results,
        )

        data_array = results.get("result", {}).get("data_array", []) if isinstance(results, dict) else []
        sources = [row[2] for row in data_array if len(row) > 2]
        logger.info("retrieval.documents_found=%s", len(data_array))
        logger.info("retrieval.sources=%s", sources)
        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
        logger.info("retrieval.response_time=%s", elapsed_ms)
        logger.info("retrieval.end elapsed_ms=%s", elapsed_ms)
        return results if isinstance(results, dict) else {"result": {"data_array": []}}

    def search(self, query):
        rows = self.retrieve_context(query, num_results=5).get("result", {}).get("data_array", [])
        return [
            {
                "chunk_id": row[0] if len(row) > 0 else "",
                "text": row[1] if len(row) > 1 else "",
                "source_document": row[2] if len(row) > 2 else "",
                "categorie": row[3] if len(row) > 3 else "",
                "score": row[4] if len(row) > 4 else 0.0,
            }
            for row in rows
        ]

    def retrieve(self, query):
        return self.search(query)


def retrieve_context(question: str, num_results: int = 5):
    agent = RetrievalAgent()
    return agent.retrieve_context(question=question, num_results=num_results)