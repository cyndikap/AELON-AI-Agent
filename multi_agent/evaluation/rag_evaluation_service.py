from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

from multi_agent.data_access.databricks_sql_client import DatabricksSQLClient


class RAGEvaluationService:
    TABLE_NAME = "fr_raise.rag_pipeline.rag_evaluation"

    def __init__(self, sql_client: DatabricksSQLClient | None = None) -> None:
        self.sql_client = sql_client or DatabricksSQLClient()
        self._table_ready = False

    def ensure_table(self) -> None:
        if self._table_ready:
            return

        create_sql = f"""
CREATE TABLE IF NOT EXISTS {self.TABLE_NAME} (
    evaluation_id STRING,
    executed_at TIMESTAMP,
    dataset_name STRING,
    question_id STRING,
    question STRING,
    expected_category STRING,
    predicted_category STRING,
    reference_answer STRING,
    answer STRING,
    expected_sources_json STRING,
    expected_keywords_json STRING,
    sources_json STRING,
    categories_json STRING,
    category_match INT,
    source_match_rate DOUBLE,
    keyword_match_rate DOUBLE,
    retrieval_count INT,
    retrieval_success INT,
    response_time_ms DOUBLE,
    relevance_score DOUBLE,
    faithfulness_score DOUBLE,
    hallucination_rate DOUBLE,
    answer_quality DOUBLE,
    compliance_score DOUBLE,
    created_at TIMESTAMP
)
USING DELTA
"""
        self.sql_client.execute(create_sql)

        # Backward-compatible migration for pre-existing tables.
        alter_sql = f"""
ALTER TABLE {self.TABLE_NAME}
ADD COLUMNS (
    expected_sources_json STRING,
    expected_keywords_json STRING,
    category_match INT,
    source_match_rate DOUBLE,
    keyword_match_rate DOUBLE
)
"""
        try:
            self.sql_client.execute(alter_sql)
        except Exception:
            # Columns may already exist; table stays usable.
            pass
        self._table_ready = True

    def save_result(self, payload: dict) -> dict:
        self.ensure_table()
        normalized = self._normalize_payload(payload)

        insert_sql = f"""
INSERT INTO {self.TABLE_NAME} (
    evaluation_id,
    executed_at,
    dataset_name,
    question_id,
    question,
    expected_category,
    predicted_category,
    reference_answer,
    answer,
    expected_sources_json,
    expected_keywords_json,
    sources_json,
    categories_json,
    category_match,
    source_match_rate,
    keyword_match_rate,
    retrieval_count,
    retrieval_success,
    response_time_ms,
    relevance_score,
    faithfulness_score,
    hallucination_rate,
    answer_quality,
    compliance_score,
    created_at
)
SELECT
    '{self.sql_client.sql_string(normalized['evaluation_id'])}',
    CAST('{self.sql_client.sql_string(normalized['executed_at'])}' AS TIMESTAMP),
    '{self.sql_client.sql_string(normalized['dataset_name'])}',
    '{self.sql_client.sql_string(normalized['question_id'])}',
    '{self.sql_client.sql_string(normalized['question'])}',
    '{self.sql_client.sql_string(normalized['expected_category'])}',
    '{self.sql_client.sql_string(normalized['predicted_category'])}',
    '{self.sql_client.sql_string(normalized['reference_answer'])}',
    '{self.sql_client.sql_string(normalized['answer'])}',
    '{self.sql_client.sql_string(normalized['expected_sources_json'])}',
    '{self.sql_client.sql_string(normalized['expected_keywords_json'])}',
    '{self.sql_client.sql_string(normalized['sources_json'])}',
    '{self.sql_client.sql_string(normalized['categories_json'])}',
    {normalized['category_match']},
    {normalized['source_match_rate']},
    {normalized['keyword_match_rate']},
    {normalized['retrieval_count']},
    {normalized['retrieval_success']},
    {normalized['response_time_ms']},
    {normalized['relevance_score']},
    {normalized['faithfulness_score']},
    {normalized['hallucination_rate']},
    {normalized['answer_quality']},
    {normalized['compliance_score']},
    CAST('{self.sql_client.sql_string(normalized['created_at'])}' AS TIMESTAMP)
"""
        self.sql_client.execute(insert_sql)
        return normalized

    def latest_summary(self) -> dict:
        self.ensure_table()
        summary_sql = f"""
WITH latest_run AS (
    SELECT max(executed_at) AS executed_at
    FROM {self.TABLE_NAME}
),
base AS (
    SELECT *
    FROM {self.TABLE_NAME}
    WHERE executed_at = (SELECT executed_at FROM latest_run)
),
coverage AS (
    SELECT
        COUNT(DISTINCT CASE WHEN retrieval_success = 1 THEN expected_category END) AS covered_categories,
        COUNT(DISTINCT expected_category) AS total_categories
    FROM base
)
SELECT
    COUNT(*) AS total_questions,
    AVG(CAST(retrieval_success AS DOUBLE)) * 100.0 AS retrieval_success_rate,
    AVG(CAST(category_match AS DOUBLE)) * 100.0 AS category_match_rate,
    AVG(source_match_rate) * 100.0 AS source_match_rate,
    AVG(keyword_match_rate) * 100.0 AS keyword_match_rate,
    AVG(response_time_ms) AS avg_response_time,
    AVG(CAST(retrieval_count AS DOUBLE)) AS avg_chunks_retrieved,
    CASE
        WHEN (SELECT total_categories FROM coverage) = 0 THEN 0.0
        ELSE (SELECT covered_categories FROM coverage) * 100.0 / (SELECT total_categories FROM coverage)
    END AS category_coverage,
    AVG(answer_quality) AS avg_answer_quality,
    AVG(faithfulness_score) AS avg_faithfulness_score,
    AVG(relevance_score) AS avg_relevance_score,
    CAST((SELECT executed_at FROM latest_run) AS STRING) AS latest_run_at
FROM base
"""
        rows = self.sql_client.query_data_array(summary_sql)
        if not rows:
            return {
                "total_questions": 0,
                "retrieval_success_rate": 0.0,
                "category_match_rate": 0.0,
                "source_match_rate": 0.0,
                "keyword_match_rate": 0.0,
                "avg_response_time": 0.0,
                "avg_chunks_retrieved": 0.0,
                "category_coverage": 0.0,
                "avg_answer_quality": 0.0,
                "avg_faithfulness_score": 0.0,
                "avg_relevance_score": 0.0,
                "latest_run_at": None,
            }

        row = rows[0]
        return {
            "total_questions": int(row[0] or 0),
            "retrieval_success_rate": round(float(row[1] or 0.0), 2),
            "category_match_rate": round(float(row[2] or 0.0), 2),
            "source_match_rate": round(float(row[3] or 0.0), 2),
            "keyword_match_rate": round(float(row[4] or 0.0), 2),
            "avg_response_time": round(float(row[5] or 0.0), 2),
            "avg_chunks_retrieved": round(float(row[6] or 0.0), 2),
            "category_coverage": round(float(row[7] or 0.0), 2),
            "avg_answer_quality": round(float(row[8] or 0.0), 2),
            "avg_faithfulness_score": round(float(row[9] or 0.0), 2),
            "avg_relevance_score": round(float(row[10] or 0.0), 2),
            "latest_run_at": row[11],
        }

    def latest_details(self) -> list[dict]:
        self.ensure_table()
        details_sql = f"""
WITH latest_run AS (
    SELECT max(executed_at) AS executed_at
    FROM {self.TABLE_NAME}
)
SELECT
    question_id,
    question,
    expected_category,
    predicted_category,
    category_match,
    source_match_rate,
    keyword_match_rate,
    retrieval_success,
    retrieval_count,
    response_time_ms,
    answer_quality,
    faithfulness_score,
    relevance_score
FROM {self.TABLE_NAME}
WHERE executed_at = (SELECT executed_at FROM latest_run)
ORDER BY question_id
"""
        rows = self.sql_client.query_data_array(details_sql)
        details = []
        for row in rows:
            details.append({
                "question_id": row[0],
                "question": row[1],
                "expected_category": row[2],
                "predicted_category": row[3],
                "category_match": int(row[4] or 0),
                "source_match_rate": round(float(row[5] or 0.0) * 100.0, 2),
                "keyword_match_rate": round(float(row[6] or 0.0) * 100.0, 2),
                "retrieval_success": int(row[7] or 0),
                "retrieval_count": int(row[8] or 0),
                "response_time_ms": round(float(row[9] or 0.0), 2),
                "answer_quality": round(float(row[10] or 0.0), 2),
                "faithfulness_score": round(float(row[11] or 0.0), 2),
                "relevance_score": round(float(row[12] or 0.0), 2),
            })
        return details

    @staticmethod
    def _normalize_payload(payload: dict) -> dict:
        now = datetime.now(timezone.utc).isoformat()
        expected_sources = payload.get("expected_sources") or []
        expected_keywords = payload.get("expected_keywords") or []
        sources = payload.get("sources") or []
        categories = payload.get("categories") or []
        return {
            "evaluation_id": str(payload.get("evaluation_id") or uuid.uuid4()),
            "executed_at": str(payload.get("executed_at") or now),
            "dataset_name": str(payload.get("dataset_name") or "rag_reference_questions"),
            "question_id": str(payload.get("question_id") or "unknown"),
            "question": str(payload.get("question") or ""),
            "expected_category": str(payload.get("expected_category") or "autre"),
            "predicted_category": str(payload.get("predicted_category") or "autre"),
            "reference_answer": str(payload.get("reference_answer") or ""),
            "answer": str(payload.get("answer") or ""),
            "expected_sources_json": json.dumps([str(item) for item in expected_sources], ensure_ascii=False),
            "expected_keywords_json": json.dumps([str(item) for item in expected_keywords], ensure_ascii=False),
            "sources_json": json.dumps([str(item) for item in sources], ensure_ascii=False),
            "categories_json": json.dumps([str(item) for item in categories], ensure_ascii=False),
            "category_match": int(payload.get("category_match") or 0),
            "source_match_rate": float(payload.get("source_match_rate") or 0.0),
            "keyword_match_rate": float(payload.get("keyword_match_rate") or 0.0),
            "retrieval_count": int(payload.get("retrieval_count") or 0),
            "retrieval_success": int(payload.get("retrieval_success") or 0),
            "response_time_ms": float(payload.get("response_time_ms") or 0.0),
            "relevance_score": float(payload.get("relevance_score") or 0.0),
            "faithfulness_score": float(payload.get("faithfulness_score") or 0.0),
            "hallucination_rate": float(payload.get("hallucination_rate") or 0.0),
            "answer_quality": float(payload.get("answer_quality") or 0.0),
            "compliance_score": float(payload.get("compliance_score") or 0.0),
            "created_at": str(payload.get("created_at") or now),
        }
