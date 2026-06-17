import os
import json
import requests
import numpy as np
import chromadb
from sentence_transformers import SentenceTransformer

class LogRAG:
    def __init__(
        self,
        mcp_url="http://127.0.0.1:8000",
        embedding_model="sentence-transformers/all-MiniLM-L6-v2"
    ):
        """
        RAG Layer for logs retrieved from the MCP server.
        """
        self.mcp_url = mcp_url
        self.token = os.getenv("MCP_TOKEN")
        
        if not self.token:
            raise RuntimeError("Environment variable MCP_TOKEN not set.")

        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

        # Lazy load embedding model (only when needed)
        self.embedding_model_name = embedding_model
        self.model = None

        # Vector store structures
        self.index = None
        self.log_map = {}  # Maps FAISS index IDs ? log data
        self.dimension = 384  # all-MiniLM-L6-v2 embedding dimension

    def _ensure_model_loaded(self):
        """Lazy load the embedding model when first needed."""
        if self.model is None:
            self.model = SentenceTransformer(self.embedding_model_name)

    # -------------------------------------------------------------------
    # Helper: GET logs from MCP
    # -------------------------------------------------------------------
    def fetch_logs(self):
        response = requests.get(f"{self.mcp_url}/logs", headers=self.headers)
        response.raise_for_status()
        return response.json()["logs"]

    # -------------------------------------------------------------------
    # Convert logs to normalized text for embeddings
    # -------------------------------------------------------------------
    def log_to_text(self, log):
        """
        Convert a log entry to a compact text string.
        """
        return (
            f"Log ID: {log['id']}. "
            f"Service: {log['service']}. "
            f"Severity: {log['severity']}. "
            f"Message: {log['message']}. "
            f"Timestamp: {log['timestamp']}."
        )

    # -------------------------------------------------------------------
    # Build vector store (FAISS index)
    # -------------------------------------------------------------------
    def build_vector_store(self):
        logs = self.fetch_logs()

        if not logs:
            raise ValueError("No logs fetched from MCP server.")

        # Convert logs to text chunks
        texts = [self.log_to_text(log) for log in logs]

        # Embed texts
        self._ensure_model_loaded()
        embeddings = self.model.encode(texts, convert_to_numpy=True)

        # Initiate FAISS index
        self.index = faiss.IndexFlatL2(self.dimension)

        # Add vectors
        self.index.add(embeddings)

        # Map index â†’ log content
        self.log_map = {i: logs[i] for i in range(len(logs))}

        return len(logs)

    # -------------------------------------------------------------------
    # Similarity search API
    # -------------------------------------------------------------------
    def search(self, query_text, top_k=3):
        if self.index is None:
            raise RuntimeError("Vector store not built. Call build_vector_store() first.")

        # Compute query embedding
        self._ensure_model_loaded()
        query_vec = self.model.encode([query_text], convert_to_numpy=True)

        # Run search
        distances, indices = self.index.search(query_vec, top_k)

        results = []
        for score, idx in zip(distances[0], indices[0]):
            if idx in self.log_map:
                results.append({
                    "score": float(score),
                    "log": self.log_map[idx]
                })
        return results

    # -------------------------------------------------------------------
    # Explain anomaly (simple version)
    # -------------------------------------------------------------------
    def explain_anomaly(self, query_text, top_k=3):
        """
        Performs a similarity search and returns a structured explanation.
        """
        matches = self.search(query_text, top_k=top_k)

        explanation = {
            "query": query_text,
            "top_matches": matches,
            "summary": self._summarize(matches)
        }

        return explanation

    # -------------------------------------------------------------------
    # Internal summarization logic (no LLM yet)
    # -------------------------------------------------------------------
    def _summarize(self, matches):
        if not matches:
            return "No similar events found in historical logs."

        services = set([m["log"]["service"] for m in matches])
        severities = set([m["log"]["severity"] for m in matches])

        return (
            f"Found {len(matches)} similar historical events. "
            f"Common services involved: {', '.join(services)}. "
            f"Severity levels observed: {', '.join(severities)}. "
            f"These may indicate a recurring pattern."
        )