document.addEventListener('DOMContentLoaded', async () => {
  const kpiGrid = document.getElementById('analyticsKpiGrid');
  const lineChartEl = document.getElementById('conversationsLineChart');
  const categoriesPieEl = document.getElementById('categoriesPieChart');
  const sourcesBarEl = document.getElementById('sourcesBarChart');
  const sentimentsDonutEl = document.getElementById('sentimentsDonutChart');
  const synthesisEl = document.getElementById('analyticsSynthesis');
  const guideEl = document.getElementById('aelonGuidePanel');
  const lineAnalysisEl = document.getElementById('analyticsLineAnalysis');
  const categoryAnalysisEl = document.getElementById('analyticsCategoryAnalysis');
  const sourcesAnalysisEl = document.getElementById('analyticsSourcesAnalysis');
  const sentimentAnalysisEl = document.getElementById('analyticsSentimentAnalysis');

  const toneByIndex = ['tone-blue', 'tone-amber', 'tone-red', 'tone-violet', 'tone-green', 'tone-navy'];
  let currentViewMode = 'business';
  let lastDashboardSnapshot = null;

  if (window.AelonExplainability?.renderGuide) {
    window.AelonExplainability.renderGuide(guideEl);
  }

  if (window.AelonExplainability?.bindViewMode) {
    window.AelonExplainability.bindViewMode((mode) => {
      currentViewMode = mode;
      if (lastDashboardSnapshot) {
        renderKpis(lastDashboardSnapshot);
      }
    });
  }

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

  const KPI_META = {
    totalConversations: {
      title: 'Conversations analysees',
      details: {
        meaning: 'Indique le volume total de conversations clients prises en compte dans le pilotage.',
        why: 'Plus le volume est eleve, plus vous avez une vision fiable des besoins clients.',
        formula: 'Nombre de conversations enregistrees sur la periode selectionnee.',
        action: 'Verifier que les canaux principaux sont bien collectes pour eviter un biais de lecture.',
      },
    },
    avgResponseTime: {
      title: 'Temps moyen de reponse',
      details: {
        meaning: 'Mesure le delai moyen pour fournir une reponse a un client.',
        why: 'Une latence elevee degrade l experience client et augmente les escalades.',
        formula: 'Somme des temps de reponse / Nombre total de conversations.',
        action: 'Prioriser l optimisation des flux sur les demandes les plus frequentes.',
      },
    },
    fraudAlerts: {
      title: 'Alertes fraude',
      details: {
        meaning: 'Nombre de conversations detectees comme potentiellement frauduleuses.',
        why: 'Permet d anticiper le risque client et de proteger les comptes sensibles.',
        formula: 'Nombre de conversations marquees is_fraud = true.',
        action: 'Renforcer les guardrails sur les intents sensibles et les messages d alerte.',
      },
    },
    dominantSentiment: {
      title: 'Sentiment dominant',
      details: {
        meaning: 'Emotion la plus frequente exprimee par les clients.',
        why: 'Aide a detecter une degradation de la satisfaction ou un pic d inquietude.',
        formula: 'Categorie de sentiment avec la frequence la plus elevee.',
        action: 'Adapter les parcours et messages si le sentiment negatif progresse.',
      },
    },
    usedSources: {
      title: 'Sources utilisees',
      details: {
        meaning: 'Nombre de sources documentaires mobilisees par l IA.',
        why: 'Garantit que les reponses s appuient sur un socle documentaire vivant.',
        formula: 'Nombre de sources distinctes citees sur la periode.',
        action: 'Elargir les sources de reference pour couvrir les sujets emergents.',
      },
    },
    topCategory: {
      title: 'Bonne comprehension du sujet',
      details: {
        meaning: 'Theme de demande le plus frequent identifie dans les conversations.',
        why: 'Permet de prioriser les feuilles de route produit et support.',
        formula: 'Categorie avec le volume de conversations le plus eleve.',
        action: 'Concentrer les efforts d amelioration sur cette categorie en priorite.',
      },
    },
  };

  const renderKpis = ({ analytics, rows, categories, sentiments, sources }) => {
    const fraudCount = rows.filter((row) => !!row?.is_fraud).length;
    const cards = [
      {
        id: 'totalConversations',
        icon: '📊',
        businessLabel: 'Conversations analysees',
        technicalLabel: 'Total Conversations',
        tooltip: 'Volume total de conversations traitees.',
        value: formatNumber(analytics.total_conversations || rows.length),
        score: 90,
      },
      {
        id: 'avgResponseTime',
        icon: '⚡',
        businessLabel: 'Reactivite des reponses',
        technicalLabel: 'Average Response Time',
        tooltip: 'Temps moyen necessaire pour repondre.',
        value: formatMs(analytics.avg_response_time_ms || average(rows.map((row) => Number(row.response_time_ms || 0)))),
        score: Math.max(0, 100 - Math.round((analytics.avg_response_time_ms || average(rows.map((row) => Number(row.response_time_ms || 0)))) / 40)),
      },
      {
        id: 'fraudAlerts',
        icon: '🚨',
        businessLabel: 'Alertes fraude detectees',
        technicalLabel: 'Fraud Alerts',
        tooltip: 'Signalements potentiellement frauduleux identifies.',
        value: formatNumber(fraudCount),
        score: Math.max(35, 90 - Math.min(70, fraudCount * 5)),
      },
      {
        id: 'dominantSentiment',
        icon: '😊',
        businessLabel: 'Ressenti client dominant',
        technicalLabel: 'Dominant Sentiment',
        tooltip: 'Emotion la plus frequente dans les echanges.',
        value: dominantSentiment(sentiments),
        score: dominantSentiment(sentiments).toLowerCase().includes('neg') ? 55 : 82,
      },
      {
        id: 'usedSources',
        icon: '📚',
        businessLabel: 'Sources documentaires mobilisees',
        technicalLabel: 'Distinct Sources Used',
        tooltip: 'Nombre de sources distinctes utilisees.',
        value: formatNumber(sources.length),
        score: Math.min(100, 55 + (sources.length * 9)),
      },
      {
        id: 'topCategory',
        icon: '🏷️',
        businessLabel: 'Bonne comprehension du sujet',
        technicalLabel: 'Top Category',
        tooltip: 'Categorie de demandes la plus frequente.',
        value: topCategory(categories),
        score: 78,
      },
    ];

    kpiGrid.innerHTML = '';
    cards.forEach((card, index) => {
      const item = document.createElement('article');
      item.className = `analytics-kpi-card aelon-kpi-clickable ${toneByIndex[index % toneByIndex.length]}`;
      item.setAttribute('data-kpi-id', card.id);
      item.setAttribute('data-kpi-score', String(Math.round(Number(card.score || 0))));
      const label = currentViewMode === 'technical' ? card.technicalLabel : card.businessLabel;
      item.innerHTML = `
        <div class="analytics-kpi-topline" style="display:flex;justify-content:space-between;gap:0.5rem;align-items:flex-start;">
          <div class="analytics-kpi-icon">${card.icon}</div>
          <button type="button" class="aelon-kpi-help" data-tooltip="${card.tooltip}">ⓘ</button>
        </div>
        <div class="analytics-kpi-label">${label}</div>
        <div class="analytics-kpi-value">${card.value}</div>
      `;
      kpiGrid.appendChild(item);
    });

    if (window.AelonExplainability?.setupKpiInteractions) {
      window.AelonExplainability.setupKpiInteractions(kpiGrid, (id) => KPI_META[id]);
    }
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

    lastDashboardSnapshot = { analytics, rows, categories, sentiments, sources };

    if (window.AelonExplainability?.renderSynthesis) {
      const warnings = [];
      if (escaladeRate > 30) warnings.push('Le taux d escalade depasse 30%, signe que certaines demandes necessitent plus de precision contextuelle.');
      if (fraudCount > 0) warnings.push(`${fraudCount} alertes fraude detectees, a suivre de pres avec les equipes risque.`);
      window.AelonExplainability.renderSynthesis(synthesisEl, {
        positives: [
          `${formatNumber(analytics.total_conversations || rows.length)} conversations analysees sur la periode.`,
          `${formatNumber(sources.length)} sources documentaires mobilisees pour appuyer les reponses.`,
        ],
        warnings,
        priorityAction: escaladeRate > 30
          ? 'Ameliorer la couverture documentaire des cas complexes pour reduire les escalades.'
          : 'Conserver la dynamique actuelle et renforcer les categories les plus frequentes.',
      });
    }

    if (lineAnalysisEl) {
      lineAnalysisEl.textContent = `🤖 Analyse AELON: l activite conversationnelle montre ${lineSeries.length} points de mesure. Les pics representent les moments ou la demande client est la plus forte.`;
    }
    if (categoryAnalysisEl) {
      categoryAnalysisEl.textContent = `🤖 Analyse AELON: la categorie dominante est "${topCategory(categories)}", ce qui guide les priorites d amelioration metier.`;
    }
    if (sourcesAnalysisEl) {
      sourcesAnalysisEl.textContent = `🤖 Analyse AELON: ${sources.length} sources differentes ont ete sollicitees, un signal cle pour la fiabilite des reponses.`;
    }
    if (sentimentAnalysisEl) {
      sentimentAnalysisEl.textContent = `🤖 Analyse AELON: le sentiment dominant est "${dominantSentiment(sentiments)}". Ce signal aide a anticiper la satisfaction client.`;
    }

    if (window.CopilotAssistant?.create) {
      window.CopilotAssistant.create({
        mode: 'analytics',
        questions: [
          'Pourquoi certains indicateurs sont faibles ?',
          'Quelles actions metier prioriser cette semaine ?',
          'Quel est le principal risque client actuellement ?',
          'Quels indicateurs necessitent une attention immediate ?',
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
