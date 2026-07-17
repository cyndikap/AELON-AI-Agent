import json, os, chromadb
from azure_embeddings import AzureEmbeddingClient
from multi_agent.privacy.privacy_agent import PrivacyAgent

PROCESSED_PATH = "data/processed/logs_clean.json"
PRIVACY_AGENT = PrivacyAgent()


def _safe_text(value: str) -> str:
    return PRIVACY_AGENT.process(value, language="fr").get("anonymized_text", str(value or ""))


def _sanitize_record(record: dict) -> dict:
    safe = dict(record or {})
    for field in ("message", "query", "response", "description"):
        if field in safe and isinstance(safe[field], str):
            safe[field] = _safe_text(safe[field])
    return safe

def load_to_delta(docs: list[dict], table_name: str = "banking.tickets_clean") -> int:
    """Minimal placeholder for Delta persistence.

    Returns the number of documents received so pipeline callers can keep
    predictable behavior even when Delta write is not configured yet.
    """
    _ = table_name
    return len(docs or [])

def load_to_json(records: list):
    os.makedirs("data/processed", exist_ok=True)
    safe_records = [_sanitize_record(r) if isinstance(r, dict) else r for r in (records or [])]
    with open(PROCESSED_PATH, "w", encoding="utf-8") as f:
        json.dump(safe_records, f, ensure_ascii=False, indent=2)

def load_to_chroma(records: list) -> int:
    client     = AzureEmbeddingClient()
    chroma     = chromadb.PersistentClient(path="data/chroma")
    collection = chroma.get_or_create_collection("log_vectors", metadata={"hnsw:space": "cosine"})

    existing   = set(collection.get()["ids"])
    safe_records = [_sanitize_record(r) for r in (records or []) if isinstance(r, dict)]
    new_records = [r for r in safe_records if r["id"] not in existing]
    if not new_records:
        return 0

    texts = [
        f"Service: {r['service']}. Severity: {r['severity']}. "
        f"Catégorie: {r['category']}. Message: {r['message']}."
        for r in new_records
    ]
    embeddings = client.embed(texts)
    collection.add(
        ids=[r["id"] for r in new_records],
        documents=texts,
        embeddings=embeddings,
        metadatas=new_records,
    )
    return len(new_records)
