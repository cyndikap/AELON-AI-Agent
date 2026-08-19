#C'est le fichier qui fait le lien: DATA ENGINEERING → INTELLIGENCE ARTIFICIELLE

import csv
import json
from pathlib import Path


class DatabricksConnector:
    """
    Connecteur de données productif : lit les données métier depuis des fichiers
    structurés, avec un fallback local si le backend Databricks n'est pas disponible.
    """

    def __init__(self, base_dir: str | None = None):
        root = Path(base_dir) if base_dir else Path(__file__).resolve().parents[2]
        self.root = root
        self.data_dir = root / "data"

    def _load_csv(self):
        csv_path = self.data_dir / "bank_transactions_data_2.csv"
        if not csv_path.exists():
            return []

        with csv_path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            rows = []
            for row in reader:
                text_parts = []
                for key, value in row.items():
                    if value and str(value).strip():
                        text_parts.append(f"{key}: {value}")
                rows.append({"text": " | ".join(text_parts)})
            return rows

    def _load_json(self):
        processed_path = self.data_dir / "processed" / "logs_clean.json"
        if not processed_path.exists():
            return []

        try:
            with processed_path.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except Exception:
            return []

        if not isinstance(payload, list):
            return []

        rows = []
        for item in payload:
            if not isinstance(item, dict):
                continue
            text = item.get("message") or item.get("query") or item.get("response") or ""
            if text:
                rows.append({"text": str(text)})
        return rows

    def load_data(self):
        csv_rows = self._load_csv()
        if csv_rows:
            return csv_rows
        return self._load_json() or [
            {"text": "client cannot login"},
            {"text": "payment failed for order #1234"},
            {"text": "how to reset my password?"},
            {"text": "fraud detected on account"},
        ]