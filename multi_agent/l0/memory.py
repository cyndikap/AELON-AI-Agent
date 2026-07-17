import json
from pathlib import Path

MEMORY_PATH = Path(__file__).resolve().parents[2] / "data" / "l0_memory.json"

class L0Memory:
    def __init__(self):
        if not MEMORY_PATH.exists():
            MEMORY_PATH.parent.mkdir(parents=True, exist_ok=True)
            MEMORY_PATH.write_text("[]", encoding="utf-8")

    def load(self):
        return json.loads(MEMORY_PATH.read_text(encoding="utf-8"))

    def add(self, entry: dict):
        memory = self.load()
        memory.append(entry)
        MEMORY_PATH.write_text(
            json.dumps(memory, indent=2),
            encoding="utf-8"
        )

    def search(self, query: str):
        memory = self.load()
        results = []

        query_words = query.lower().split()

        for m in memory:
            mem_text = m.get("query", "").lower()

            # match partiel (plus intelligent)
            if any(word in mem_text for word in query_words):
                results.append(m)

        return results[:3]   # limiter pour éviter bruit