import csv
import os
import json
from pathlib import Path

import requests
import chromadb
from chromadb.config import Settings
from azure_embeddings import AzureEmbeddingClient
from multi_agent.privacy.privacy_agent import PrivacyAgent

RAG_STATE_PATH = "data/rag_state.json"


class LogRAG:
    def __init__(self, mcp_url="http://127.0.0.1:8000"):
        self.mcp_url = mcp_url
        self.privacy_agent = PrivacyAgent()
        self.token = os.getenv("MCP_TOKEN")
        self.use_local_fallback = False

        try:
            self.embedding_client = AzureEmbeddingClient()
        except Exception:
            self.embedding_client = None
            self.use_local_fallback = True

        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        } if self.token else {}

        try:
            self.chroma = chromadb.PersistentClient(path="data/chroma")
            self.collection = self.chroma.get_or_create_collection(
                name="log_vectors",
                metadata={"hnsw:space": "cosine"}
            )
        except Exception:
            self.collection = None
            self.use_local_fallback = True

        # Load RAG state
        self.indexed_log_ids = self._load_state()
        self._fallback_documents = self._load_local_documents()

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
    def _load_local_documents(self):
        possible_paths = [
            Path("data/processed/logs_clean.json"),
            Path("data/documents.csv"),
            Path("knowledge_base/it_support_kb.md"),
        ]

        for path in possible_paths:
            if not path.exists():
                continue
            try:
                if path.suffix == ".json":
                    with open(path, "r", encoding="utf-8") as handle:
                        payload = json.load(handle)
                    if isinstance(payload, list):
                        return payload
                elif path.suffix == ".csv":
                    with open(path, "r", encoding="utf-8", newline="") as handle:
                        reader = csv.DictReader(handle)
                        return list(reader)
                else:
                    return [{"text": path.read_text(encoding="utf-8", errors="ignore")}]
            except Exception:
                continue
        return [
            {"text": "client cannot login"},
            {"text": "payment failed for order #1234"},
            {"text": "how to reset my password?"},
            {"text": "fraud detected on account"},
        ]

    def fetch_logs(self):
        if not self.token or not self.mcp_url:
            return self._fallback_documents

        try:
            response = requests.get(f"{self.mcp_url}/logs", headers=self.headers, timeout=10)
            response.raise_for_status()
            payload = response.json()
            logs = payload.get("logs") if isinstance(payload, dict) else payload
            return logs if isinstance(logs, list) else self._fallback_documents
        except Exception:
            return self._fallback_documents

    # --------------------------------------------------
    # Log formatting
    # --------------------------------------------------
    def _safe_text(self, text: str) -> str:
        return self.privacy_agent.process(text, language="fr").get("anonymized_text", str(text or ""))

    def log_to_text(self, log):
        return (
            f"Service: {log['service']}. "
            f"Severity: {log['severity']}. "
            f"Message: {self._safe_text(log['message'])}. "
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

        safe_metadatas = []
        for log in new_logs:
            safe_log = dict(log)
            if "message" in safe_log:
                safe_log["message"] = self._safe_text(safe_log["message"])
            safe_metadatas.append(safe_log)

        self.collection.add(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=safe_metadatas
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
        safe_query = self._safe_text(query)
        if self.use_local_fallback or self.collection is None or self.embedding_client is None:
            matches = []
            for item in self._fallback_documents:
                text = item.get("text") if isinstance(item, dict) else str(item)
                if safe_query.lower() in text.lower():
                    matches.append({"score": 1.0, "log": item})
            return matches[:top_k]

        query_embedding = self.embedding_client.embed([safe_query])

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
