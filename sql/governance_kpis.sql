MERGE INTO fr_raise.rag_pipeline.governance_metrics AS tgt
USING (
    WITH base AS (
        SELECT
            CAST(timestamp AS DATE) AS metric_date,
            answer,
            sources,
            retrieval_count
        FROM fr_raise.rag_pipeline.gold_conversations
    ),
    base_metrics AS (
        SELECT
            metric_date,
            SUM(CASE WHEN size(coalesce(sources, array())) > 0 THEN 1 ELSE 0 END) AS responses_with_sources,
            SUM(CASE WHEN size(coalesce(sources, array())) = 0 THEN 1 ELSE 0 END) AS responses_without_sources,
            AVG(CAST(retrieval_count AS DOUBLE)) AS avg_documents_retrieved,
            AVG(CASE WHEN retrieval_count > 0 THEN 1.0 ELSE 0.0 END) AS retrieval_success_ratio,
            AVG(CASE WHEN retrieval_count = 0 THEN 1.0 ELSE 0.0 END) AS retrieval_empty_ratio,
            AVG(CAST(length(coalesce(answer, '')) AS DOUBLE)) AS avg_context_chars
        FROM base
        GROUP BY metric_date
    ),
    citations_per_source AS (
        SELECT
            metric_date,
            to_json(
                map_from_entries(
                    collect_list(named_struct('key', source_name, 'value', cnt))
                )
            ) AS citations_per_source_json
        FROM (
            SELECT
                b.metric_date,
                s AS source_name,
                COUNT(*) AS cnt
            FROM base b
            LATERAL VIEW explode(coalesce(b.sources, array())) exploded AS s
            GROUP BY b.metric_date, s
        ) x
        GROUP BY metric_date
    )
    SELECT
        m.metric_date,
        m.responses_with_sources,
        m.responses_without_sources,
        m.avg_documents_retrieved,
        m.retrieval_success_ratio,
        m.retrieval_empty_ratio,
        m.avg_context_chars,
        coalesce(c.citations_per_source_json, '{}') AS citations_per_source_json,
        current_timestamp() AS updated_at
    FROM base_metrics m
    LEFT JOIN citations_per_source c ON m.metric_date = c.metric_date
) AS src
ON tgt.metric_date = src.metric_date
WHEN MATCHED THEN UPDATE SET
    tgt.responses_with_sources = src.responses_with_sources,
    tgt.responses_without_sources = src.responses_without_sources,
    tgt.avg_documents_retrieved = src.avg_documents_retrieved,
    tgt.retrieval_success_ratio = src.retrieval_success_ratio,
    tgt.retrieval_empty_ratio = src.retrieval_empty_ratio,
    tgt.avg_context_chars = src.avg_context_chars,
    tgt.citations_per_source_json = src.citations_per_source_json,
    tgt.updated_at = src.updated_at
WHEN NOT MATCHED THEN INSERT (
    metric_date,
    responses_with_sources,
    responses_without_sources,
    avg_documents_retrieved,
    retrieval_success_ratio,
    retrieval_empty_ratio,
    avg_context_chars,
    citations_per_source_json,
    updated_at
) VALUES (
    src.metric_date,
    src.responses_with_sources,
    src.responses_without_sources,
    src.avg_documents_retrieved,
    src.retrieval_success_ratio,
    src.retrieval_empty_ratio,
    src.avg_context_chars,
    src.citations_per_source_json,
    src.updated_at
);

SELECT *
FROM fr_raise.rag_pipeline.governance_metrics
ORDER BY metric_date DESC;
