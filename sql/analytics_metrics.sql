CREATE TABLE IF NOT EXISTS fr_raise.rag_pipeline.analytics_metrics (
    metric_date DATE,
    total_conversations BIGINT,
    questions_count BIGINT,
    avg_chunks_retrieved DOUBLE,
    avg_response_time_ms DOUBLE,
    top_queries_json STRING,
    category_counts_json STRING,
    source_counts_json STRING,
    updated_at TIMESTAMP
)
USING DELTA;
