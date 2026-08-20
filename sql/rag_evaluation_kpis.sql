WITH latest_run AS (
    SELECT max(executed_at) AS executed_at
    FROM fr_raise.rag_pipeline.rag_evaluation
),
base AS (
    SELECT *
    FROM fr_raise.rag_pipeline.rag_evaluation
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
    AVG(relevance_score) AS avg_relevance_score
FROM base
