document.addEventListener('DOMContentLoaded', async () => {
  const kpiGrid = document.getElementById('analyticsKpiGrid');
  const history = document.getElementById('analyticsChatHistory');
  const questionsByDayPanel = document.getElementById('questionsByDayPanel');
  const responseTimePanel = document.getElementById('responseTimePanel');
  const categoriesPanel = document.getElementById('categoriesPanel');
  const topSourcesList = document.getElementById('topSourcesList');

  const formatNumber = (value) => {
    const num = Number(value || 0);
    return Number.isFinite(num) ? num.toLocaleString('fr-FR') : '0';
  };

  const formatMs = (value) => {
    const num = Number(value || 0);
    return Number.isFinite(num) ? `${Math.round(num)} ms` : '0 ms';
  };

  const showFallback = (message) => {
    const bubble = document.createElement('div');
    bubble.className = 'analytics-chat-message';
    bubble.textContent = message;
    history.appendChild(bubble);
  };

  try {
    const response = await fetch('/analytics');
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();
    const topCategories = Array.isArray(data.top_categories) ? data.top_categories : [];
    const topSources = Array.isArray(data.top_sources) ? data.top_sources : [];
    const topQueries = Array.isArray(data.top_queries) ? data.top_queries : [];

    const metrics = [
      { label: 'Conversations', value: formatNumber(data.total_conversations), tone: 'blue' },
      { label: 'Temps réponse moyen', value: formatMs(data.avg_response_time_ms), tone: 'orange' },
      { label: 'Chunks moyens', value: String(Number(data.avg_chunks_retrieved || 0).toFixed(2)), tone: 'green' },
      { label: 'Top catégories', value: String(topCategories.length), tone: 'red' },
    ];

    metrics.forEach((metric) => {
      const card = document.createElement('div');
      card.className = `analytics-kpi-card ${metric.tone}`;
      card.innerHTML = `<span>${metric.label}</span><strong>${metric.value}</strong>`;
      kpiGrid.appendChild(card);
    });

    const insights = [];
    insights.push(`Questions/jour: ${Array.isArray(data.questions_by_day) ? data.questions_by_day.length : 0} points`);
    insights.push(`Top source: ${topSources[0] ? topSources[0].source : 'N/A'}`);
    insights.push(`Top catégorie: ${topCategories[0] ? (topCategories[0].category || topCategories[0].label) : 'N/A'}`);
    insights.push(`Top requête: ${topQueries[0] ? (topQueries[0].question || '') : 'N/A'}`);

    insights.forEach((entry) => {
      const bubble = document.createElement('div');
      bubble.className = 'analytics-chat-message';
      bubble.textContent = entry;
      history.appendChild(bubble);
    });

    const days = Array.isArray(data.questions_by_day) ? data.questions_by_day : [];
    questionsByDayPanel.textContent = days.length
      ? days.map((item) => `${item.day}: ${item.count}`).join(' | ')
      : 'Aucune donnée journalière disponible';

    responseTimePanel.textContent = `Temps moyen: ${formatMs(data.avg_response_time_ms)}`;

    categoriesPanel.textContent = topCategories.length
      ? topCategories.map((item) => `${item.category || item.label}: ${item.count}`).join(' | ')
      : 'Aucune catégorie disponible';

    if (topSourcesList) {
      topSourcesList.innerHTML = '';
      if (topSources.length === 0) {
        const item = document.createElement('div');
        item.className = 'analytics-list-item';
        item.innerHTML = '<span>Aucune source</span><strong>-</strong>';
        topSourcesList.appendChild(item);
      } else {
        topSources.forEach((sourceItem) => {
          const item = document.createElement('div');
          item.className = 'analytics-list-item';
          item.innerHTML = `<span>${sourceItem.source}</span><strong>${sourceItem.count}</strong>`;
          topSourcesList.appendChild(item);
        });
      }
    }
  } catch (error) {
    showFallback('Impossible de charger les KPI Analytics pour le moment.');
    if (questionsByDayPanel) questionsByDayPanel.textContent = 'Indisponible';
    if (responseTimePanel) responseTimePanel.textContent = 'Indisponible';
    if (categoriesPanel) categoriesPanel.textContent = 'Indisponible';
  }

  const chips = document.querySelectorAll('.analytics-prompt-chip');
  chips.forEach((chip) => {
    chip.addEventListener('click', () => {
      const msg = chip.dataset.question || chip.textContent.trim();
      const bubble = document.createElement('div');
      bubble.className = 'analytics-chat-message user';
      bubble.textContent = msg;
      history.appendChild(bubble);
    });
  });
});
