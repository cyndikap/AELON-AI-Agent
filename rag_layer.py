import os
import json
import requests
import chromadb
from chromadb.config import Settings
from azure_embeddings import AzureEmbeddingClient

RAG_STATE_PATH = "data/rag_state.json"


class LogRAG:
    def __init__(self, mcp_url="http://127.0.0.1:8000"):
        self.mcp_url = mcp_url
        self.embedding_client = AzureEmbeddingClient()

        self.token = os.getenv("MCP_TOKEN")
        if not self.token:
            raise RuntimeError("MCP_TOKEN not set")

        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

        # Vector Store
        self.chroma = chromadb.PersistentClient(
          path="data/chroma")

        self.collection = self.chroma.get_or_create_collection(
            name="log_vectors",
            metadata={"hnsw:space": "cosine"}
        )

        # Load RAG state
        self.indexed_log_ids = self._load_state()

    # --------------------------------------------------
    # State management
    # --------------------------------------------------
    def _load_state(self) -> set:
        if not os.path.exists(RAG_STATE_PATH):
            return set()
        with open(RAG_STATE_PATH, "r") as f:
            data = json.load(f)
            return set(data.get("indexed_log_ids", []))

    def _save_state(self):
        with open(RAG_STATE_PATH, "w") as f:
            json.dump(
                {"indexed_log_ids": list(self.indexed_log_ids)},
                f,
                indent=2
            )

    # --------------------------------------------------
    # MCP fetch
    # --------------------------------------------------
    def fetch_logs(self):
        response = requests.get(f"{self.mcp_url}/logs", headers=self.headers)
        response.raise_for_status()
        return response.json()["logs"]

    # --------------------------------------------------
    # Log formatting
    # --------------------------------------------------
    def log_to_text(self, log):
        return (
            f"Service: {log['service']}. "
            f"Severity: {log['severity']}. "
            f"Message: {log['message']}. "
            f"Timestamp: {log['timestamp']}."
        )

    # --------------------------------------------------
    # Incremental refresh
    # --------------------------------------------------
    def incremental_refresh(self):
        logs = self.fetch_logs()

        # Detect NEW logs
        new_logs = [
            log for log in logs
            if str(log["id"]) not in self.indexed_log_ids
        ]

        if not new_logs:
            print("✅ RAG already up to date (no new logs)")
            return 0

        texts = [self.log_to_text(log) for log in new_logs]
        embeddings = self.embedding_client.embed(texts)
        ids = [str(log["id"]) for log in new_logs]

        self.collection.add(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=new_logs
        )

        # Update state
        for log in new_logs:
            self.indexed_log_ids.add(str(log["id"]))

        self._save_state()

        print(f"✅ Incrementally indexed {len(new_logs)} new logs")
        return len(new_logs)

    # --------------------------------------------------
    # Search
    # --------------------------------------------------
    def search(self, query: str, top_k: int = 3):
        query_embedding = self.embedding_client.embed([query])

        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=top_k
        )

        matches = []
        for meta, dist in zip(
            results.get("metadatas", [[]])[0],
            results.get("distances", [[]])[0]
        ):
            matches.append({
                "score": float(dist),
                "log": meta
            })

        return matches
