document.addEventListener('DOMContentLoaded', async () => {
  const kpiGrid = document.getElementById('analyticsKpiGrid');
  const lineChartEl = document.getElementById('conversationsLineChart');
  const categoriesPieEl = document.getElementById('categoriesPieChart');
  const sourcesBarEl = document.getElementById('sourcesBarChart');
  const sentimentsDonutEl = document.getElementById('sentimentsDonutChart');

  const toneByIndex = ['tone-blue', 'tone-amber', 'tone-red', 'tone-violet', 'tone-green', 'tone-navy'];

  const formatNumber = (value) => {
    const num = Number(value || 0);
    return Number.isFinite(num) ? num.toLocaleString('fr-FR') : '0';
  };

  const formatMs = (value) => {
    const num = Number(value || 0);
    return Number.isFinite(num) ? `${Math.round(num)} ms` : '0 ms';
  };

  const safeArray = (value) => (Array.isArray(value) ? value : []);

  const aggregateCounts = (rows, key, fallback = 'autre') => {
    const map = new Map();
    rows.forEach((row) => {
      const label = String(row?.[key] || fallback).trim() || fallback;
      map.set(label, (map.get(label) || 0) + 1);
    });
    return [...map.entries()]
      .map(([label, count]) => ({ label, count }))
      .sort((a, b) => b.count - a.count);
  };

  const aggregateByDay = (rows) => {
    const map = new Map();
    rows.forEach((row) => {
      const stamp = String(row?.timestamp || '');
      const day = stamp.slice(0, 10) || 'unknown';
      map.set(day, (map.get(day) || 0) + 1);
    });
    return [...map.entries()]
      .map(([day, count]) => ({ day, count }))
      .sort((a, b) => a.day.localeCompare(b.day));
  };

  const dominantSentiment = (sentiments) => {
    if (!sentiments.length) return 'N/A';
    return sentiments[0].label;
  };

  const topCategory = (categories) => {
    if (!categories.length) return 'N/A';
    return categories[0].label;
  };

  const renderKpis = ({ analytics, rows, categories, sentiments, sources }) => {
    const fraudCount = rows.filter((row) => !!row?.is_fraud).length;
    const cards = [
      { icon: '📊', label: 'Conversations analysees', value: formatNumber(analytics.total_conversations || rows.length) },
      { icon: '⚡', label: 'Temps moyen de reponse', value: formatMs(analytics.avg_response_time_ms || average(rows.map((row) => Number(row.response_time_ms || 0)))) },
      { icon: '🚨', label: 'Alertes fraude', value: formatNumber(fraudCount) },
      { icon: '😊', label: 'Sentiment dominant', value: dominantSentiment(sentiments) },
      { icon: '📚', label: 'Sources utilisees', value: formatNumber(sources.length) },
      { icon: '🎯', label: 'Top categorie', value: topCategory(categories) },
    ];

    kpiGrid.innerHTML = '';
    cards.forEach((card, index) => {
      const item = document.createElement('article');
      item.className = `analytics-kpi-card ${toneByIndex[index % toneByIndex.length]}`;
      item.innerHTML = `
        <div class="analytics-kpi-icon">${card.icon}</div>
        <div class="analytics-kpi-label">${card.label}</div>
        <div class="analytics-kpi-value">${card.value}</div>
      `;
      kpiGrid.appendChild(item);
    });
  };

  const average = (values) => {
    const nums = values.filter((v) => Number.isFinite(v));
    if (!nums.length) return 0;
    return nums.reduce((acc, value) => acc + value, 0) / nums.length;
  };

  const plotLine = (series) => {
    if (!window.Plotly || !lineChartEl) return;
    const x = series.map((item) => item.day);
    const y = series.map((item) => item.count);
    Plotly.newPlot(
      lineChartEl,
      [{ x, y, type: 'scatter', mode: 'lines+markers', line: { color: '#0a3d91', width: 3 }, marker: { color: '#2f8df7', size: 7 } }],
      {
        margin: { t: 24, r: 18, b: 44, l: 42 },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        xaxis: { title: 'Jour' },
        yaxis: { title: 'Conversations' },
      },
      { responsive: true }
    );
  };

  const plotCategoriesPie = (categories) => {
    if (!window.Plotly || !categoriesPieEl) return;
    Plotly.newPlot(
      categoriesPieEl,
      [{ labels: categories.map((item) => item.label), values: categories.map((item) => item.count), type: 'pie', textinfo: 'label+percent' }],
      { margin: { t: 24, r: 12, b: 12, l: 12 }, paper_bgcolor: 'rgba(0,0,0,0)' },
      { responsive: true }
    );
  };

  const plotSourcesBar = (sources) => {
    if (!window.Plotly || !sourcesBarEl) return;
    Plotly.newPlot(
      sourcesBarEl,
      [{ x: sources.map((item) => item.label), y: sources.map((item) => item.count), type: 'bar', marker: { color: '#1f67da' } }],
      {
        margin: { t: 24, r: 12, b: 42, l: 42 },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        xaxis: { title: 'Source' },
        yaxis: { title: 'Volume de citations' },
      },
      { responsive: true }
    );
  };

  const plotSentimentsDonut = (sentiments) => {
    if (!window.Plotly || !sentimentsDonutEl) return;
    Plotly.newPlot(
      sentimentsDonutEl,
      [{ labels: sentiments.map((item) => item.label), values: sentiments.map((item) => item.count), type: 'pie', hole: 0.58 }],
      { margin: { t: 24, r: 12, b: 12, l: 12 }, paper_bgcolor: 'rgba(0,0,0,0)' },
      { responsive: true }
    );
  };

  const answerTemplate = (question, context) => {
    const { fraudCount, escaladeRate, dominant, topCategoryLabel } = context;

    if (question.includes('fraudes')) {
      return `Les alertes fraude progressent principalement quand les clients mentionnent des operations sensibles. Le volume actuel est de ${fraudCount}, ce qui suggere de renforcer la prevention proactive et les scripts de verification.`;
    }
    if (question.includes('escalades')) {
      return `Le taux d'escalade estime est de ${escaladeRate}%. Cela indique des parcours ou la reponse automatique atteint ses limites. Priorite: enrichir la base de connaissances sur les cas complexes.`;
    }
    if (question.includes('frequents')) {
      return `Les sujets les plus frequents se concentrent autour de la categorie ${topCategoryLabel}. Le sentiment dominant est ${dominant}. Cela oriente les efforts vers des workflows de resolution plus rapides.`;
    }
    return `Les categories a action metier immediate sont celles a plus fort volume et forte sensibilite client. En tete: ${topCategoryLabel}. Recommandation: plan d'action combine support, conformite et communication client.`;
  };

  try {
    const [analyticsResponse, rowsResponse] = await Promise.all([
      fetch('/analytics'),
      fetch('/web/analytics/data'),
    ]);

    if (!analyticsResponse.ok || !rowsResponse.ok) {
      throw new Error('analytics fetch error');
    }

    const analytics = await analyticsResponse.json();
    const rowsPayload = await rowsResponse.json();
    const rows = safeArray(rowsPayload.rows);

    const categoriesFromRows = aggregateCounts(rows, 'category', 'autre');
    const categoriesFromApi = safeArray(analytics.top_categories).map((item) => ({
      label: String(item.category || item.label || 'autre'),
      count: Number(item.count || 0),
    }));
    const categories = categoriesFromRows.length ? categoriesFromRows : categoriesFromApi;

    const sentiments = aggregateCounts(rows, 'sentiment', 'neutral');
    const sourcesFromRows = aggregateCounts(rows.flatMap((row) => safeArray(row.privacy_entities).map((entity) => ({ source: entity.entity_type }))), 'source', 'source');
    const sourcesFromApi = safeArray(analytics.top_sources).map((item) => ({
      label: String(item.source || 'source'),
      count: Number(item.count || 0),
    }));
    const sources = sourcesFromApi.length ? sourcesFromApi : sourcesFromRows;

    const byDay = aggregateByDay(rows);
    const lineSeries = byDay.length
      ? byDay
      : safeArray(analytics.questions_by_day).map((item) => ({ day: String(item.day || ''), count: Number(item.count || 0) }));

    renderKpis({ analytics, rows, categories, sentiments, sources });
    plotLine(lineSeries);
    plotCategoriesPie(categories.slice(0, 8));
    plotSourcesBar(sources.slice(0, 8));
    plotSentimentsDonut(sentiments.slice(0, 8));

    const fraudCount = rows.filter((row) => !!row.is_fraud).length;
    const escaladeRate = rows.length ? Math.round((rows.filter((row) => !!row.escalated).length / rows.length) * 100) : 0;
    const context = {
      fraudCount,
      escaladeRate,
      dominant: dominantSentiment(sentiments),
      topCategoryLabel: topCategory(categories),
    };

    if (window.CopilotAssistant?.create) {
      window.CopilotAssistant.create({
        mode: 'analytics',
        questions: [
          'Pourquoi les fraudes augmentent ?',
          'Quelles categories progressent ?',
          'Quels sujets sont les plus frequents ?',
          'Quels problemes utilisateurs reviennent souvent ?',
        ],
        initialMessage: 'Selectionnez une question pour afficher une analyse metier.',
        onAsk: async (question) => {
          try {
            const res = await fetch('/web/analytics/chat', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ question }),
            });

            if (!res.ok) {
              throw new Error(`HTTP ${res.status}`);
            }

            const payload = await res.json();
            return String(payload.answer || '').trim() || answerTemplate(question, context);
          } catch (_error) {
            return answerTemplate(question, context);
          }
        },
      });
    }
  } catch (_error) {
    const fallback = 'Impossible de charger les donnees analytics pour le moment. Verifiez la connectivite et les sources de donnees.';
    if (kpiGrid) {
      kpiGrid.innerHTML = `<article class="analytics-kpi-card tone-red"><div class="analytics-kpi-icon">⚠️</div><div class="analytics-kpi-label">Disponibilite</div><div class="analytics-kpi-value">Indisponible</div></article>`;
    }
    [lineChartEl, categoriesPieEl, sourcesBarEl, sentimentsDonutEl].forEach((el) => {
      if (el) el.textContent = fallback;
    });
    if (window.CopilotAssistant?.create) {
      window.CopilotAssistant.create({
        mode: 'analytics',
        questions: [
          'Pourquoi les fraudes augmentent ?',
          'Quelles categories progressent ?',
          'Quels sujets sont les plus frequents ?',
          'Quels problemes utilisateurs reviennent souvent ?',
        ],
        initialMessage: fallback,
        onAsk: async () => fallback,
      });
    }
  }
});
