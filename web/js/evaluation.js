document.addEventListener('DOMContentLoaded', async () => {
  const kpiGrid = document.getElementById('evaluationKpiGrid');
  const coveragePanel = document.getElementById('evaluationCoveragePanel');
  const responsePanel = document.getElementById('evaluationResponsePanel');
  const chunksPanel = document.getElementById('evaluationChunksPanel');
  const detailsList = document.getElementById('evaluationDetailsList');
  const insightHistory = document.getElementById('evaluationInsightHistory');

  const addInsight = (text) => {
    const bubble = document.createElement('div');
    bubble.className = 'analytics-chat-message';
    bubble.textContent = text;
    insightHistory.appendChild(bubble);
  };

  try {
    const response = await fetch('/evaluation');
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();
    const metrics = [
      { label: 'Questions évaluées', value: String(data.total_questions || 0), tone: 'blue' },
      { label: 'Retrieval success', value: `${Number(data.retrieval_success_rate || 0).toFixed(2)}%`, tone: 'green' },
      { label: 'Category match', value: `${Number(data.category_match_rate || 0).toFixed(2)}%`, tone: 'orange' },
      { label: 'Source match', value: `${Number(data.source_match_rate || 0).toFixed(2)}%`, tone: 'red' },
      { label: 'Keyword match', value: `${Number(data.keyword_match_rate || 0).toFixed(2)}%`, tone: 'blue' },
      { label: 'Temps moyen', value: `${Math.round(Number(data.avg_response_time || 0))} ms`, tone: 'green' },
    ];

    metrics.forEach((metric) => {
      const card = document.createElement('div');
      card.className = `analytics-kpi-card ${metric.tone}`;
      card.innerHTML = `<span>${metric.label}</span><strong>${metric.value}</strong>`;
      kpiGrid.appendChild(card);
    });

    coveragePanel.textContent = `Couverture: ${Number(data.category_coverage || 0).toFixed(2)}%`;
    responsePanel.textContent = `Latence moyenne: ${Math.round(Number(data.avg_response_time || 0))} ms`;
    chunksPanel.textContent = `Chunks moyens: ${Number(data.avg_chunks_retrieved || 0).toFixed(2)}`;

    const details = Array.isArray(data.details) ? data.details : [];
    detailsList.innerHTML = '';
    if (details.length === 0) {
      const item = document.createElement('div');
      item.className = 'analytics-list-item';
      item.innerHTML = '<span>Aucune évaluation disponible</span><strong>-</strong>';
      detailsList.appendChild(item);
    } else {
      details.forEach((detail) => {
        const item = document.createElement('div');
        item.className = 'analytics-list-item';
        item.innerHTML = `<span>${detail.question_id} · ${detail.expected_category} · src ${Number(detail.source_match_rate || 0).toFixed(0)}% · kw ${Number(detail.keyword_match_rate || 0).toFixed(0)}%</span><strong>${detail.retrieval_count} chunks</strong>`;
        detailsList.appendChild(item);
      });
    }

    addInsight(`Dernier run: ${data.latest_run_at || 'N/A'}`);
    addInsight(`Qualité moyenne: ${Number(data.avg_answer_quality || 0).toFixed(2)}`);
    addInsight(`Faithfulness moyenne: ${Number(data.avg_faithfulness_score || 0).toFixed(2)}`);
    addInsight(`Relevance moyenne: ${Number(data.avg_relevance_score || 0).toFixed(2)}`);
    addInsight(`Category match: ${Number(data.category_match_rate || 0).toFixed(2)}%`);
    addInsight(`Source match: ${Number(data.source_match_rate || 0).toFixed(2)}%`);
    addInsight(`Keyword match: ${Number(data.keyword_match_rate || 0).toFixed(2)}%`);
  } catch (error) {
    coveragePanel.textContent = 'Indisponible';
    responsePanel.textContent = 'Indisponible';
    chunksPanel.textContent = 'Indisponible';
    addInsight('Impossible de charger les métriques d’évaluation RAG.');
  }
});
