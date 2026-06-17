import json
from collections import Counter

PROCESSED_PATH = "data/processed/logs_clean.json"

class AnalyticsAgent:
    """Analyse les données ETL pour produire des KPIs SAV bancaire."""

    def _load(self) -> list[dict]:
        try:
            with open(PROCESSED_PATH, encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def get_summary(self) -> dict:
        records = self._load()
        if not records:
            return {"error": "Aucune donnée disponible. Lancez le pipeline ETL d'abord."}

        severities = Counter(r["severity"] for r in records)
        categories = Counter(r["category"] for r in records)
        errors = [r for r in records if r["severity"] == "ERROR"]
        top_services = Counter(r["service"] for r in errors).most_common(3)

        return {
            "total_logs": len(records),
            "severity_distribution": dict(severities),
            "category_distribution": dict(categories),
            "error_rate": round(severities.get("ERROR", 0) / len(records), 2),
            "top_error_services": top_services,
        }

    def get_customer_profile(self, customer_id: str) -> dict:
        records = [r for r in self._load() if r.get("customer_id") == customer_id]
        if not records:
            return {"customer_id": customer_id, "incidents": 0}
        return {
            "customer_id": customer_id,
            "incidents": len(records),
            "severity_distribution": dict(Counter(r["severity"] for r in records)),
            "affected_services": list({r["service"] for r in records}),
        }
