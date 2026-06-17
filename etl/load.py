import json, os, chromadb
from azure_embeddings import AzureEmbeddingClient

PROCESSED_PATH = "data/processed/logs_clean.json"

def load_to_delta (docs: list[dict], table_name: str = "banking.tickets_clean"):

def load_to_json(records: list):
    os.makedirs("data/processed", exist_ok=True)
    with open(PROCESSED_PATH, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

def load_to_chroma(records: list) -> int:
    client     = AzureEmbeddingClient()
    chroma     = chromadb.PersistentClient(path="data/chroma")
    collection = chroma.get_or_create_collection("log_vectors", metadata={"hnsw:space": "cosine"})

    existing   = set(collection.get()["ids"])
    new_records = [r for r in records if r["id"] not in existing]
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
