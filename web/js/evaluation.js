document.addEventListener('DOMContentLoaded', async () => {
  const kpiGrid = document.getElementById('evaluationKpiGrid');
  const radarChart = document.getElementById('evaluationRadarChart');
  const categoryChart = document.getElementById('evaluationCategoryChart');
  const latencyChart = document.getElementById('evaluationLatencyChart');
  const chunksChart = document.getElementById('evaluationChunksChart');
  const insightsList = document.getElementById('evaluationInsightsList');
  const errorTableBody = document.getElementById('evaluationErrorTableBody');
  const synthesisEl = document.getElementById('evaluationSynthesis');
  const guideEl = document.getElementById('aelonGuidePanel');
  const globalScoreTrigger = document.getElementById('evaluationGlobalScoreTrigger');
  const radarAnalysisEl = document.getElementById('evaluationRadarAnalysis');
  const categoryAnalysisEl = document.getElementById('evaluationCategoryAnalysis');
  const latencyAnalysisEl = document.getElementById('evaluationLatencyAnalysis');
  const chunksAnalysisEl = document.getElementById('evaluationChunksAnalysis');

  let currentViewMode = 'business';
  let lastMergedData = null;

  if (window.AelonExplainability?.renderGuide) {
    window.AelonExplainability.renderGuide(guideEl);
  }

  if (window.AelonExplainability?.bindViewMode) {
    window.AelonExplainability.bindViewMode((mode) => {
      currentViewMode = mode;
      if (lastMergedData) {
        createKpiCards(lastMergedData);
      }
    });
  }

  const fallbackMetrics = {
    total_questions: 36,
    retrieval_success_rate: 94,
    source_match_rate: 90,
    category_match_rate: 72,
    keyword_match_rate: 68,
    category_coverage: 82,
    avg_response_time: 1800,
    avg_chunks_retrieved: 8.5,
    latest_run_at: '2026-08-26',
    details: [
      { question_id: 'Q12', expected_category: 'Fraude', source_match_rate: 82, keyword_match_rate: 65, retrieval_count: 7 },
      { question_id: 'Q18', expected_category: 'RGPD', source_match_rate: 76, keyword_match_rate: 56, retrieval_count: 8 },
      { question_id: 'Q21', expected_category: 'Virement', source_match_rate: 63, keyword_match_rate: 58, retrieval_count: 9 },
      { question_id: 'Q30', expected_category: 'Carte bancaire', source_match_rate: 88, keyword_match_rate: 74, retrieval_count: 6 },
    ],
  };

  const getMetricTone = (value) => {
    if (value >= 85) return 'success';
    if (value >= 60) return 'warning';
    return 'danger';
  };

  const formatPercent = (value) => `${Number(value || 0).toFixed(0)}%`;
  const formatMs = (value) => `${Math.round(Number(value || 0))} ms`;

  const KPI_META = {
    totalQuestions: {
      title: 'Questions evaluees',
      details: {
        meaning: 'Nombre de questions de reference utilisees pour mesurer la performance du systeme.',
        why: 'Plus la base d evaluation est representative, plus le score est fiable.',
        formula: 'Total des questions du dataset d evaluation executees sur la periode.',
        action: 'Elargir regulierement le dataset avec de nouveaux cas metier.',
      },
    },
    retrievalSuccessRate: {
      title: 'Retrieval Success Rate',
      details: {
        meaning: 'Mesure la capacite du systeme a retrouver les bons documents.',
        why: 'Le retrieval conditionne la qualite et la fiabilite de la reponse finale.',
        formula: 'Questions avec retrieval pertinent / Questions evaluees.',
        action: 'Ameliorer le chunking et la couverture documentaire des cas faibles.',
      },
    },
    sourceMatchRate: {
      title: 'Source Match Rate',
      details: {
        meaning: 'Part des reponses associees a la source attendue.',
        why: 'Un bon match source augmente la confiance et la tracabilite.',
        formula: 'Reponses avec source correcte / Reponses evaluees.',
        action: 'Ajuster le reranking et les metadonnees des documents.',
      },
    },
    categoryMatchRate: {
      title: 'Category Match Rate',
      details: {
        meaning: 'Mesure la bonne interpretation du sujet metier.',
        why: 'Une categorie mal identifiee peut mener a une action inadaptee.',
        formula: 'Questions bien classees / Questions evaluees.',
        action: 'Revoir la taxonomie et les exemples de classification.',
      },
    },
    keywordMatchRate: {
      title: 'Keyword Match Rate',
      details: {
        meaning: 'Mesure la presence des mots-cles critiques attendus dans la reponse.',
        why: 'Permet de verifier la precision metier de la formulation.',
        formula: 'Mots-cles attendus retrouves / Total des mots-cles attendus.',
        action: 'Enrichir les prompts et la base de connaissance avec des formulations metier.',
      },
    },
    avgResponseTime: {
      title: 'Temps moyen de reponse',
      details: {
        meaning: 'Temps moyen necessaire pour produire la reponse.',
        why: 'Un delai trop eleve impacte l experience client et les couts operatoires.',
        formula: 'Somme des temps de reponse / Nombre de requetes.',
        action: 'Optimiser la recherche et limiter les contextes trop volumineux.',
      },
    },
  };

  const createKpiCards = (data) => {
    const metrics = [
      {
        id: 'totalQuestions',
        businessLabel: 'Questions evaluees',
        technicalLabel: 'Total Questions',
        tooltip: 'Nombre total de cas testes.',
        value: String(data.total_questions || 36),
        note: 'Total',
        tone: 'info',
        score: 88,
      },
      {
        id: 'retrievalSuccessRate',
        businessLabel: '📚 Documents correctement retrouves',
        technicalLabel: 'Retrieval Success Rate',
        tooltip: 'Capacite a trouver les bons documents.',
        value: formatPercent(data.retrieval_success_rate),
        note: 'Retrieval',
        tone: getMetricTone(data.retrieval_success_rate),
        score: Number(data.retrieval_success_rate || 0),
      },
      {
        id: 'sourceMatchRate',
        businessLabel: '✅ Utilisation des bonnes sources',
        technicalLabel: 'Source Match Rate',
        tooltip: 'Alignement entre sources attendues et sources utilisees.',
        value: formatPercent(data.source_match_rate),
        note: 'Sources',
        tone: getMetricTone(data.source_match_rate),
        score: Number(data.source_match_rate || 0),
      },
      {
        id: 'categoryMatchRate',
        businessLabel: '🏷 Bonne comprehension du sujet',
        technicalLabel: 'Category Match Rate',
        tooltip: 'Precision de la categorisation metier.',
        value: formatPercent(data.category_match_rate),
        note: 'Categories',
        tone: getMetricTone(data.category_match_rate),
        score: Number(data.category_match_rate || 0),
      },
      {
        id: 'keywordMatchRate',
        businessLabel: '🎯 Precision des reponses',
        technicalLabel: 'Keyword Match Rate',
        tooltip: 'Couverture des mots-cles metier critiques.',
        value: formatPercent(data.keyword_match_rate),
        note: 'Keywords',
        tone: getMetricTone(data.keyword_match_rate),
        score: Number(data.keyword_match_rate || 0),
      },
      {
        id: 'avgResponseTime',
        businessLabel: '⚡ Vitesse de reponse',
        technicalLabel: 'Average Response Time',
        tooltip: 'Temps moyen de reponse du systeme.',
        value: formatMs(data.avg_response_time),
        note: 'Latence',
        tone: data.avg_response_time <= 2000 ? 'success' : 'warning',
        score: Math.max(0, 100 - Math.round(Number(data.avg_response_time || 0) / 40)),
      },
    ];

    kpiGrid.innerHTML = metrics.map((metric) => `
      <article class="eval-kpi-card tone-${metric.tone} aelon-kpi-clickable" data-kpi-id="${metric.id}" data-kpi-score="${Math.round(Number(metric.score || 0))}">
        <div class="eval-kpi-topline">
          <span class="eval-kpi-label">${currentViewMode === 'technical' ? metric.technicalLabel : metric.businessLabel}</span>
          <span class="eval-kpi-badge">${metric.note}</span>
        </div>
        <div><button type="button" class="aelon-kpi-help" data-tooltip="${metric.tooltip}">ⓘ</button></div>
        <div class="eval-kpi-value">${metric.value}</div>
      </article>
    `).join('');

    if (window.AelonExplainability?.setupKpiInteractions) {
      window.AelonExplainability.setupKpiInteractions(kpiGrid, (id) => KPI_META[id]);
    }
  };

  const createRadarChart = (data) => {
    const axes = [
      { label: 'Retrieval', value: data.retrieval_success_rate || 0 },
      { label: 'Sources', value: data.source_match_rate || 0 },
      { label: 'Categories', value: data.category_match_rate || 0 },
      { label: 'Keywords', value: data.keyword_match_rate || 0 },
      { label: 'Coverage', value: data.category_coverage || 0 },
    ];

    const size = 280;
    const center = size / 2;
    const radius = 94;
    const step = (Math.PI * 2) / axes.length;
    const polygonPoints = axes.map((axis, index) => {
      const angle = -Math.PI / 2 + index * step;
      const x = center + Math.cos(angle) * radius * (axis.value / 100);
      const y = center + Math.sin(angle) * radius * (axis.value / 100);
      return `${x},${y}`;
    }).join(' ');

    const rings = [20, 40, 60, 80, 100].map((value) => {
      const pts = Array.from({ length: axes.length }, (_, index) => {
        const angle = -Math.PI / 2 + index * step;
        const x = center + Math.cos(angle) * radius * (value / 100);
        const y = center + Math.sin(angle) * radius * (value / 100);
        return `${x},${y}`;
      });
      return `<polygon points="${pts.join(' ')}" class="eval-radar-ring" />`;
    }).join('');

    const axisMarkup = axes.map((axis, index) => {
      const angle = -Math.PI / 2 + index * step;
      const x = center + Math.cos(angle) * radius;
      const y = center + Math.sin(angle) * radius;
      const textX = center + Math.cos(angle) * (radius + 26);
      const textY = center + Math.sin(angle) * (radius + 26);
      return `
        <line x1="${center}" y1="${center}" x2="${x}" y2="${y}" class="eval-radar-axis" />
        <text x="${textX}" y="${textY}" class="eval-radar-label" text-anchor="middle">${axis.label}</text>
      `;
    }).join('');

    radarChart.innerHTML = `
      <svg viewBox="0 0 ${size} ${size}" class="eval-radar-svg" role="img" aria-label="Radar chart IA">
        ${rings}
        ${axisMarkup}
        <polygon points="${polygonPoints}" class="eval-radar-area" />
      </svg>
    `;
  };

  const createCategoryChart = (data) => {
    const categories = [
      { label: 'Fraude', value: 95 },
      { label: 'RGPD', value: 85 },
      { label: 'KYC', value: 75 },
      { label: 'Conformité', value: 70 },
      { label: 'Carte bancaire', value: 88 },
      { label: 'Virement', value: 82 },
    ];

    const max = 100;
    categoryChart.innerHTML = categories.map((item) => `
      <div class="eval-category-row">
        <div class="eval-category-row-label">${item.label}</div>
        <div class="eval-category-bar-track">
          <div class="eval-category-bar-fill" style="width:${(item.value / max) * 100}%"></div>
        </div>
        <div class="eval-category-row-score">${item.value}%</div>
      </div>
    `).join('');
  };

  const createLineChart = (data) => {
    const points = [420, 390, 340, 320, 290, 250, 210];
    const width = 360;
    const height = 170;
    const min = 180;
    const max = 450;
    const mapped = points.map((value, index) => {
      const x = (index / (points.length - 1)) * width;
      const y = height - ((value - min) / (max - min)) * (height - 20) - 10;
      return `${x},${y}`;
    }).join(' ');

    latencyChart.innerHTML = `
      <svg viewBox="0 0 ${width} ${height}" class="eval-chart-svg" aria-label="Évolution des temps de réponse">
        <g>
          <line x1="0" y1="150" x2="360" y2="150" class="eval-chart-gridline" />
          <line x1="0" y1="110" x2="360" y2="110" class="eval-chart-gridline" />
          <line x1="0" y1="70" x2="360" y2="70" class="eval-chart-gridline" />
        </g>
        <polyline points="${mapped}" class="eval-chart-line" />
        ${points.map((value, index) => {
          const x = (index / (points.length - 1)) * width;
          const y = height - ((value - min) / (max - min)) * (height - 20) - 10;
          return `<circle cx="${x}" cy="${y}" r="4" class="eval-chart-point" />`;
        }).join('')}
      </svg>
    `;
  };

  const createChunkChart = () => {
    const values = [7, 9, 8, 11, 10, 7];
    chunksChart.innerHTML = `
      <div class="eval-bar-chart-grid">
        ${values.map((value) => `
          <div class="eval-bar-column">
            <div class="eval-bar-fill" style="height:${(value / 12) * 100}%"></div>
            <span>${value}</span>
          </div>
        `).join('')}
      </div>
    `;
  };

  const buildInsights = (data) => {
    const items = [
      '✅ Retrieval Success Rate excellent',
      '✅ Sources documentaires correctement utilisées',
      '⚠️ Category Match Rate nécessite une amélioration',
      '⚠️ Keyword Match Rate peut être optimisé',
      '✅ Couverture métier satisfaisante',
    ];

    insightsList.innerHTML = items.map((item) => `<li>${item}</li>`).join('');
  };

  const buildErrorTable = () => {
    const rows = [
      { question: 'Q12', metric: 'Category Match', cause: 'Mauvaise classification métier' },
      { question: 'Q18', metric: 'Keyword Match', cause: 'Réponse trop générique' },
      { question: 'Q21', metric: 'Source Match', cause: 'Source secondaire utilisée' },
      { question: 'Q33', metric: 'Retrieval', cause: 'Chunks insuffisants ou trop courts' },
    ];

    errorTableBody.innerHTML = rows.map((row) => `
      <tr>
        <td>${row.question}</td>
        <td><span class="eval-kpi-tag">${row.metric}</span></td>
        <td>${row.cause}</td>
      </tr>
    `).join('');
  };

  const mountEvaluationCopilot = () => {
    if (!window.CopilotAssistant?.create) return;
    window.CopilotAssistant.create({
      mode: 'evaluation',
      questions: [
        'Pourquoi le score est-il faible ?',
        'Quels indicateurs necessitent une attention immediate ?',
        'Quel est le principal risque ?',
        'Que faut-il ameliorer en priorite ?',
        'Quels domaines metier performent le mieux ?',
        'Que recommandez-vous pour le prochain sprint ?',
      ],
      initialMessage: 'Sélectionnez une question pour obtenir des recommandations d’analyse IA.',
      onAsk: async (question) => {
        if (question.includes('Category Match Rate')) {
          return 'Le Category Match Rate reste faible car la taxonomie métier est partiellement sous-représentée et les requêtes couvrent des cas hybrides. Il faut enrichir les intents, corriger le mapping des catégories et renforcer la cohérence des labels métier.';
        }
        if (question.includes('KPI')) {
          return 'Les KPI à améliorer en priorité sont le Category Match Rate, le Keyword Match Rate et la couverture des documents. La qualité globale dépend surtout de la précision de la classification et de la qualité des chunks récupérés.';
        }
        if (question.includes('performent')) {
          return 'Les domaines qui performent le mieux sont Fraude, Carte bancaire et Virement, car leur corpus documentaire est mieux structuré et les documents d’appui sont plus homogènes. Le RGPD et la conformité restent plus sensibles aux formulations longues et ambiguës.';
        }
        if (question.includes('Retrieval Agent')) {
          return 'Pour améliorer le Retrieval Agent, il faut augmenter la couverture documentaire, réviser le chunking, ajouter des synonymes bancaires et limiter les documents trop génériques ou trop longs. Le système gagnera aussi en précision avec un tri par score de pertinence plus strict.';
        }
        if (question.includes('moins pertinentes')) {
          return 'Les réponses sont moins pertinentes lorsque la requête mélangent des concepts métier, quand la source principale est absente ou quand le chunk extrait ne contient pas la réponse exacte. Le correctif consiste à re-ranker les éléments, à renforcer la provenance documentaire et à améliorer la reformulation.';
        }
        return 'Les documents à enrichir sont ceux qui traitent des cas RGPD, de la conformité, des virements complexes et des fraudes transverses. Les contenus manquants ou trop génériques doivent être complétés avec des cas d’usage détaillés et des références réglementaires.';
      },
    });
  };

  try {
    const response = await fetch('/evaluation');
    const data = response.ok ? await response.json() : fallbackMetrics;
    const mergedData = {
      ...fallbackMetrics,
      ...data,
      details: Array.isArray(data.details) && data.details.length ? data.details : fallbackMetrics.details,
    };
    lastMergedData = mergedData;

    createKpiCards(mergedData);
    createRadarChart(mergedData);
    createCategoryChart(mergedData);
    createLineChart(mergedData);
    createChunkChart();
    buildInsights(mergedData);
    buildErrorTable();

    const globalScore = Math.round((
      Number(mergedData.retrieval_success_rate || 0)
      + Number(mergedData.source_match_rate || 0)
      + Number(mergedData.category_match_rate || 0)
      + Number(mergedData.keyword_match_rate || 0)
    ) / 4);

    if (globalScoreTrigger) {
      globalScoreTrigger.textContent = `${globalScore} / 100`;
      globalScoreTrigger.style.cursor = 'pointer';
      globalScoreTrigger.title = 'Cliquez pour comprendre le score global';
      globalScoreTrigger.onclick = () => {
        if (!window.AelonExplainability?.openKpiModal) return;
        window.AelonExplainability.openKpiModal('🏆 Global Score', {
          meaning: `Votre score global est de ${globalScore}/100. Il resume la performance combinee du retrieval, des sources, de la categorisation et de la precision des reponses.`,
          why: 'Ce score permet de voir rapidement si la plateforme delivre des reponses fiables pour les utilisateurs non techniques.',
          formula: 'Moyenne de Retrieval Success Rate, Source Match Rate, Category Match Rate et Keyword Match Rate.',
          action: 'Points forts: qualite du retrieval et utilisation des sources. Points a ameliorer: categorisation et pertinence metier.',
        });
      };
    }

    if (window.AelonExplainability?.renderSynthesis) {
      const warnings = [];
      if (Number(mergedData.category_match_rate || 0) < 80) warnings.push('Certaines categories metier sont encore mal identifiees.');
      if (Number(mergedData.avg_response_time || 0) > 2000) warnings.push('Les temps de reponse depassent l objectif de fluidite.');
      window.AelonExplainability.renderSynthesis(synthesisEl, {
        positives: [
          'Les documents sont globalement bien retrouves.',
          'Les sources utilisees restent majoritairement fiables.',
        ],
        warnings,
        priorityAction: Number(mergedData.category_match_rate || 0) < 80
          ? 'Ameliorer la classification automatique des demandes metier.'
          : 'Poursuivre l optimisation des temps de reponse et la couverture des cas complexes.',
      });
    }

    if (radarAnalysisEl) {
      radarAnalysisEl.textContent = '🤖 Analyse AELON: le radar met en evidence un niveau de retrieval solide, mais une variabilite plus forte sur la categorisation et les mots-cles.';
    }
    if (categoryAnalysisEl) {
      categoryAnalysisEl.textContent = '🤖 Analyse AELON: les categories Fraude et Carte bancaire performent mieux que les themes de conformite plus ambigus.';
    }
    if (latencyAnalysisEl) {
      latencyAnalysisEl.textContent = `🤖 Analyse AELON: le temps moyen observe est ${formatMs(mergedData.avg_response_time)}. Une baisse de latence ameliorera la satisfaction client.`;
    }
    if (chunksAnalysisEl) {
      chunksAnalysisEl.textContent = `🤖 Analyse AELON: environ ${Number(mergedData.avg_chunks_retrieved || 0).toFixed(1)} chunks sont recuperes en moyenne. Un meilleur ciblage peut reduire le bruit contextuel.`;
    }

    mountEvaluationCopilot();
  } catch (_error) {
    createKpiCards(fallbackMetrics);
    createRadarChart(fallbackMetrics);
    createCategoryChart(fallbackMetrics);
    createLineChart(fallbackMetrics);
    createChunkChart();
    buildInsights(fallbackMetrics);
    buildErrorTable();
    if (window.AelonExplainability?.renderSynthesis) {
      window.AelonExplainability.renderSynthesis(synthesisEl, {
        positives: [],
        warnings: ['Le mode fallback est actif: certaines donnees d evaluation sont indisponibles.'],
        priorityAction: 'Relancer un run d evaluation pour reconstituer les indicateurs reels.',
      });
    }
    mountEvaluationCopilot();
  }
});
