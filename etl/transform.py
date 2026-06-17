from datetime import datetime

SEVERITY_MAP = {"INFO": 1, "WARNING": 2, "WARN": 2, "ERROR": 3, "CRITICAL": 4}

SERVICE_CATEGORY = {
    "paiement": "transaction", "virement": "transaction", "carte": "card",
    "authentification": "auth", "auth": "auth", "compte": "account",
    "banking": "account", "credit": "credit", "fraude": "fraud",
}

def transform(records: list) -> list:
    cleaned = []
    for r in records:
        try:
            ts = datetime.fromisoformat(str(r.get("timestamp", "")).replace("Z", ""))
            severity = r.get("severity", "INFO").upper()
            service  = r.get("service", "unknown").lower()
            cleaned.append({
                "id":             str(r.get("id", "")),
                "timestamp":      ts.isoformat(),
                "hour":           ts.hour,
                "service":        service,
                "category":       SERVICE_CATEGORY.get(service, "other"),
                "severity":       severity,
                "severity_score": SEVERITY_MAP.get(severity, 0),
                "message":        r.get("message", "").strip(),
                "customer_id":    r.get("customer_id") or None,
            })
        except (ValueError, KeyError):
            continue
    return cleaned
