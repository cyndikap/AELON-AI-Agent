CREATE TABLE IF NOT EXISTS fr_raise.rag_pipeline.governance_metrics (
    metric_date DATE,
    responses_with_sources BIGINT,
    responses_without_sources BIGINT,
    avg_documents_retrieved DOUBLE,
    retrieval_success_ratio DOUBLE,
    retrieval_empty_ratio DOUBLE,
    avg_context_chars DOUBLE,
    citations_per_source_json STRING,
    updated_at TIMESTAMP
)
USING DELTA;
