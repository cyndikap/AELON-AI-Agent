import json
import logging
import os
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from multi_agent.data_access.databricks_sql_client import DatabricksSQLClient

logger = logging.getLogger("aelon.conversation_logger")


@dataclass
class ConversationRecord:
    question: str
    answer: str
    sources: list[str]
    categories: list[str]
    retrieval_count: int
    response_time_ms: float
    user_session_id: str = "anonymous"
    conversation_id: str | None = None
    timestamp: str | None = None


class ConversationLogger:
    """Persist conversations to Databricks SQL table with local fallback."""

    def __init__(
        self,
        table_name: str = "fr_raise.rag_pipeline.gold_conversations",
        host: str | None = None,
        token: str | None = None,
        warehouse_id: str | None = None,
        fallback_path: str | None = None,
        timeout_seconds: int = 30,
    ):
        self.table_name = table_name
        self.timeout_seconds = timeout_seconds
        self._table_initialized = False
        self.sql_client = DatabricksSQLClient(
            host=host,
            token=token,
            warehouse_id=warehouse_id,
            timeout_seconds=timeout_seconds,
        )

        default_fallback = Path("data") / "processed" / "failed_conversation_events.jsonl"
        self.fallback_path = Path(fallback_path) if fallback_path else default_fallback
        self.fallback_path.parent.mkdir(parents=True, exist_ok=True)

    def save(self, record: ConversationRecord) -> dict:
        payload = self._normalize_record(record)
        return self.save_payload(payload)

    def save_payload(self, payload: dict, write_fallback_on_error: bool = True) -> dict:
        normalized = self._normalize_payload(payload)

        if not self._is_databricks_configured():
            if write_fallback_on_error:
                self._append_to_fallback(normalized, "missing_databricks_sql_config")
            return {"saved": False, "reason": "missing_databricks_sql_config", "payload": normalized}

        try:
            self._ensure_table()
            if self.conversation_exists(normalized["conversation_id"]):
                return {
                    "saved": True,
                    "conversation_id": normalized["conversation_id"],
                    "already_exists": True,
                }
            self._insert_record(normalized)
            return {"saved": True, "conversation_id": normalized["conversation_id"], "already_exists": False}
        except Exception as exc:
            logger.exception("conversation_logger.save.failed")
            if write_fallback_on_error:
                self._append_to_fallback(normalized, str(exc))
            return {
                "saved": False,
                "reason": str(exc),
                "conversation_id": normalized["conversation_id"],
            }

    def _normalize_record(self, record: ConversationRecord) -> dict:
        timestamp = record.timestamp or datetime.now(timezone.utc).isoformat()
        return {
            "conversation_id": record.conversation_id or str(uuid.uuid4()),
            "timestamp": timestamp,
            "question": str(record.question or ""),
            "answer": str(record.answer or ""),
            "sources": [str(item) for item in (record.sources or [])],
            "categories": [str(item) for item in (record.categories or [])],
            "retrieval_count": int(record.retrieval_count or 0),
            "response_time_ms": float(record.response_time_ms or 0.0),
            "user_session_id": str(record.user_session_id or "anonymous"),
        }

    def _normalize_payload(self, payload: dict) -> dict:
        timestamp = payload.get("timestamp") or datetime.now(timezone.utc).isoformat()
        return {
            "conversation_id": str(payload.get("conversation_id") or uuid.uuid4()),
            "timestamp": str(timestamp),
            "question": str(payload.get("question") or ""),
            "answer": str(payload.get("answer") or ""),
            "sources": [str(item) for item in (payload.get("sources") or [])],
            "categories": [str(item) for item in (payload.get("categories") or [])],
            "retrieval_count": int(payload.get("retrieval_count") or 0),
            "response_time_ms": float(payload.get("response_time_ms") or 0.0),
            "user_session_id": str(payload.get("user_session_id") or "anonymous"),
        }

    def _is_databricks_configured(self) -> bool:
        return self.sql_client.is_configured()

    def _ensure_table(self) -> None:
        if self._table_initialized:
            return

        expected_columns = {
            "conversation_id": "STRING",
            "timestamp": "TIMESTAMP",
            "question": "STRING",
            "answer": "STRING",
            "sources": "ARRAY<STRING>",
            "categories": "ARRAY<STRING>",
            "retrieval_count": "INT",
            "response_time_ms": "DOUBLE",
            "user_session_id": "STRING",
        }

        create_sql = f"""
CREATE TABLE IF NOT EXISTS {self.table_name} (
    conversation_id STRING,
    timestamp TIMESTAMP,
    question STRING,
    answer STRING,
    sources ARRAY<STRING>,
    categories ARRAY<STRING>,
    retrieval_count INT,
    response_time_ms DOUBLE,
    user_session_id STRING
)
USING DELTA
"""
        self.sql_client.execute(create_sql)

        try:
            describe_rows = self.sql_client.query_data_array(f"DESCRIBE TABLE {self.table_name}")
            existing = {
                str(row[0]).strip().lower()
                for row in describe_rows
                if row and str(row[0]).strip() and not str(row[0]).startswith("#")
            }
            for column_name, column_type in expected_columns.items():
                if column_name.lower() not in existing:
                    alter_sql = f"ALTER TABLE {self.table_name} ADD COLUMNS ({column_name} {column_type})"
                    self.sql_client.execute(alter_sql)
        except Exception:
            logger.exception("conversation_logger.schema_migration.failed")

        self._table_initialized = True

    def conversation_exists(self, conversation_id: str) -> bool:
        self._ensure_table()
        conversation_id = self.sql_client.sql_string(conversation_id)
        exists_sql = f"""
SELECT COUNT(*)
FROM {self.table_name}
WHERE conversation_id = '{conversation_id}'
"""
        rows = self.sql_client.query_data_array(exists_sql)
        if not rows:
            return False
        try:
            return int(rows[0][0]) > 0
        except Exception:
            return False

    def _insert_record(self, payload: dict) -> None:
        conversation_id = self.sql_client.sql_string(payload["conversation_id"])
        timestamp = self.sql_client.sql_string(payload["timestamp"])
        question = self.sql_client.sql_string(payload["question"])
        answer = self.sql_client.sql_string(payload["answer"])
        user_session_id = self.sql_client.sql_string(payload["user_session_id"])
        sources_json = self.sql_client.sql_string(json.dumps(payload["sources"], ensure_ascii=False))
        categories_json = self.sql_client.sql_string(json.dumps(payload["categories"], ensure_ascii=False))

        insert_sql = f"""
INSERT INTO {self.table_name} (
    conversation_id,
    timestamp,
    question,
    answer,
    sources,
    categories,
    retrieval_count,
    response_time_ms,
    user_session_id
)
SELECT
    '{conversation_id}' AS conversation_id,
    CAST('{timestamp}' AS TIMESTAMP) AS timestamp,
    '{question}' AS question,
    '{answer}' AS answer,
    from_json('{sources_json}', 'array<string>') AS sources,
    from_json('{categories_json}', 'array<string>') AS categories,
    {int(payload['retrieval_count'])} AS retrieval_count,
    {float(payload['response_time_ms'])} AS response_time_ms,
    '{user_session_id}' AS user_session_id
"""
        self.sql_client.execute(insert_sql)

    def _append_to_fallback(self, payload: dict, reason: str) -> None:
        event = {
            "reason": reason,
            "payload": payload,
            "saved_at": datetime.now(timezone.utc).isoformat(),
        }
        with self.fallback_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=False) + "\n")
