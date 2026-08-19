MERGE INTO fr_raise.rag_pipeline.analytics_metrics AS tgt
USING (
    WITH base AS (
        SELECT
            CAST(timestamp AS DATE) AS metric_date,
            question,
            retrieval_count,
            response_time_ms,
            categories,
            sources
        FROM fr_raise.rag_pipeline.gold_conversations
    ),
    daily AS (
        SELECT
            metric_date,
            COUNT(*) AS total_conversations,
            COUNT(*) AS questions_count,
            AVG(CAST(retrieval_count AS DOUBLE)) AS avg_chunks_retrieved,
            AVG(CAST(response_time_ms AS DOUBLE)) AS avg_response_time_ms
        FROM base
        GROUP BY metric_date
    ),
    top_queries AS (
        SELECT
            metric_date,
            to_json(
                collect_list(
                    named_struct('question', question, 'count', cnt)
                )
            ) AS top_queries_json
        FROM (
            SELECT
                metric_date,
                question,
                COUNT(*) AS cnt,
                ROW_NUMBER() OVER (
                    PARTITION BY metric_date
                    ORDER BY COUNT(*) DESC, question
                ) AS rn
            FROM base
            GROUP BY metric_date, question
        ) ranked
        WHERE rn <= 10
        GROUP BY metric_date
    ),
    category_counts AS (
        SELECT
            metric_date,
            to_json(
                map_from_entries(
                    collect_list(named_struct('key', category, 'value', cnt))
                )
            ) AS category_counts_json
        FROM (
            SELECT
                b.metric_date,
                c AS category,
                COUNT(*) AS cnt
            FROM base b
            LATERAL VIEW explode(coalesce(b.categories, array())) exploded AS c
            GROUP BY b.metric_date, c
        ) x
        GROUP BY metric_date
    ),
    source_counts AS (
        SELECT
            metric_date,
            to_json(
                map_from_entries(
                    collect_list(named_struct('key', source_name, 'value', cnt))
                )
            ) AS source_counts_json
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
        d.metric_date,
        d.total_conversations,
        d.questions_count,
        d.avg_chunks_retrieved,
        d.avg_response_time_ms,
        coalesce(t.top_queries_json, '[]') AS top_queries_json,
        coalesce(c.category_counts_json, '{}') AS category_counts_json,
        coalesce(s.source_counts_json, '{}') AS source_counts_json,
        current_timestamp() AS updated_at
    FROM daily d
    LEFT JOIN top_queries t ON d.metric_date = t.metric_date
    LEFT JOIN category_counts c ON d.metric_date = c.metric_date
    LEFT JOIN source_counts s ON d.metric_date = s.metric_date
) AS src
ON tgt.metric_date = src.metric_date
WHEN MATCHED THEN UPDATE SET
    tgt.total_conversations = src.total_conversations,
    tgt.questions_count = src.questions_count,
    tgt.avg_chunks_retrieved = src.avg_chunks_retrieved,
    tgt.avg_response_time_ms = src.avg_response_time_ms,
    tgt.top_queries_json = src.top_queries_json,
    tgt.category_counts_json = src.category_counts_json,
    tgt.source_counts_json = src.source_counts_json,
    tgt.updated_at = src.updated_at
WHEN NOT MATCHED THEN INSERT (
    metric_date,
    total_conversations,
    questions_count,
    avg_chunks_retrieved,
    avg_response_time_ms,
    top_queries_json,
    category_counts_json,
    source_counts_json,
    updated_at
) VALUES (
    src.metric_date,
    src.total_conversations,
    src.questions_count,
    src.avg_chunks_retrieved,
    src.avg_response_time_ms,
    src.top_queries_json,
    src.category_counts_json,
    src.source_counts_json,
    src.updated_at
);

SELECT *
FROM fr_raise.rag_pipeline.analytics_metrics
ORDER BY metric_date DESC;
