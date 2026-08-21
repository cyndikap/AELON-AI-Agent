document.addEventListener('DOMContentLoaded', async () => {
  const kpiGrid = document.getElementById('evaluationKpiGrid');
  const coveragePanel = document.getElementById('evaluationCoveragePanel');
  const responsePanel = document.getElementById('evaluationResponsePanel');
  const chunksPanel = document.getElementById('evaluationChunksPanel');
  const detailsList = document.getElementById('evaluationDetailsList');
  let evaluationContext = {
    categoryMatchRate: 0,
    retrievalSuccessRate: 0,
    bestDomain: 'N/A',
    sourceMatchRate: 0,
    keywordMatchRate: 0,
  };

  const localEvaluationAnswer = (question) => {
    if (question.includes('Category Match Rate')) {
      return `Le Category Match Rate (${evaluationContext.categoryMatchRate.toFixed(2)}%) baisse quand les questions couvrent des cas hors taxonomie. Il faut enrichir les categories metier et le mapping des intents.`;
    }
    if (question.includes('performent')) {
      return `Les domaines les plus performants sont ceux avec les meilleurs taux de source/keyword match. Domaine dominant estime: ${evaluationContext.bestDomain}.`;
    }
    if (question.includes('attention')) {
      return `Les KPI prioritaires sont retrieval success (${evaluationContext.retrievalSuccessRate.toFixed(2)}%), source match (${evaluationContext.sourceMatchRate.toFixed(2)}%) et keyword match (${evaluationContext.keywordMatchRate.toFixed(2)}%).`;
    }
    return `Pour ameliorer le Retrieval Success Rate, renforcez la couverture documentaire, ajustez le chunking et revoyez les regles de reformulation des requetes.`;
  };

  const mountEvaluationCopilot = () => {
    if (!window.CopilotAssistant?.create) return;
    window.CopilotAssistant.create({
      mode: 'evaluation',
      questions: [
        'Pourquoi le Category Match Rate est faible ?',
        'Quels domaines metier performent le mieux ?',
        'Quels KPI necessitent une attention particuliere ?',
        'Comment ameliorer le Retrieval Success Rate ?',
      ],
      initialMessage: 'Selectionnez une question pour interpreter les resultats d evaluation.',
      onAsk: async (question) => localEvaluationAnswer(question),
    });
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

    const domainCounts = new Map();
    details.forEach((detail) => {
      const domain = String(detail.expected_category || 'N/A');
      domainCounts.set(domain, (domainCounts.get(domain) || 0) + 1);
    });
    const bestDomain = [...domainCounts.entries()].sort((a, b) => b[1] - a[1])[0]?.[0] || 'N/A';

    evaluationContext = {
      categoryMatchRate: Number(data.category_match_rate || 0),
      retrievalSuccessRate: Number(data.retrieval_success_rate || 0),
      bestDomain,
      sourceMatchRate: Number(data.source_match_rate || 0),
      keywordMatchRate: Number(data.keyword_match_rate || 0),
    };
    mountEvaluationCopilot();
  } catch (error) {
    coveragePanel.textContent = 'Indisponible';
    responsePanel.textContent = 'Indisponible';
    chunksPanel.textContent = 'Indisponible';
    mountEvaluationCopilot();
  }
});
