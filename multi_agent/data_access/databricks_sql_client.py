import os
import time
from typing import Any

import requests


class DatabricksSQLClient:
    def __init__(
        self,
        host: str | None = None,
        token: str | None = None,
        warehouse_id: str | None = None,
        timeout_seconds: int = 30,
    ):
        self.host = (host or os.getenv("DATABRICKS_HOST", "")).rstrip("/")
        self.token = token or os.getenv("DATABRICKS_TOKEN", "")
        self.warehouse_id = warehouse_id or os.getenv("DATABRICKS_SQL_WAREHOUSE_ID", "")
        self.timeout_seconds = timeout_seconds

    def is_configured(self) -> bool:
        return bool(self.host and self.token and self.warehouse_id)

    def execute(self, statement: str, wait_timeout: str = "30s") -> dict[str, Any]:
        if not self.is_configured():
            raise RuntimeError("Databricks SQL client is not configured")

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        submit_url = f"{self.host}/api/2.0/sql/statements"
        body = {
            "warehouse_id": self.warehouse_id,
            "statement": statement,
            "wait_timeout": wait_timeout,
        }

        response = requests.post(
            submit_url,
            headers=headers,
            json=body,
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()

        if payload.get("status", {}).get("state") == "SUCCEEDED":
            return payload

        statement_id = payload.get("statement_id")
        if not statement_id:
            raise RuntimeError(f"Databricks SQL statement failed without statement_id: {payload}")

        status_url = f"{self.host}/api/2.0/sql/statements/{statement_id}"
        started = time.perf_counter()

        while True:
            status_resp = requests.get(
                status_url,
                headers=headers,
                timeout=self.timeout_seconds,
            )
            status_resp.raise_for_status()
            status_payload = status_resp.json()
            state = status_payload.get("status", {}).get("state", "")

            if state == "SUCCEEDED":
                return status_payload
            if state in {"FAILED", "CANCELED", "CLOSED"}:
                message = status_payload.get("status", {}).get("error", {}).get("message", "unknown error")
                raise RuntimeError(f"Databricks SQL statement {state}: {message}")
            if (time.perf_counter() - started) > self.timeout_seconds:
                raise TimeoutError("Databricks SQL statement polling timeout")

            time.sleep(0.5)

    def query_data_array(self, statement: str) -> list[list[Any]]:
        payload = self.execute(statement)
        return payload.get("result", {}).get("data_array", [])

    @staticmethod
    def sql_string(value: str) -> str:
        return str(value).replace("'", "''")
