document.addEventListener('DOMContentLoaded', async () => {
  const governanceKpiGrid = document.getElementById('governanceKpiGrid');
  const governanceAgentsBody = document.getElementById('governanceAgentsBody');
  const governanceTopSourcesChart = document.getElementById('governanceTopSourcesChart');
  const governanceTopDocumentsChart = document.getElementById('governanceTopDocumentsChart');
  const governanceUnusedDocumentsChart = document.getElementById('governanceUnusedDocumentsChart');
  const governanceUnusedDocs = document.getElementById('governanceUnusedDocs');
  const governanceThresholds = document.getElementById('governanceThresholds');
  const governanceAlertsList = document.getElementById('governanceAlertsList');
  const governanceRecommendations = document.getElementById('governanceRecommendations');
  const governanceResetThresholds = document.getElementById('governanceResetThresholds');

  const formatPercent = (value) => `${Number(value || 0).toFixed(2)}%`;
  const formatInteger = (value) => String(Math.round(Number(value || 0)));
  const formatMs = (value) => `${Math.round(Number(value || 0))} ms`;
  const alertStorageKey = 'aelon-governance-thresholds-v1';

  const defaultThresholds = {
    retrievalSuccessRate: { label: 'Retrieval Success Rate', orange: 85, red: 70 },
    sourceMatchRate: { label: 'Source Match Rate', orange: 80, red: 65 },
    categoryMatchRate: { label: 'Category Match Rate', orange: 80, red: 60 },
    keywordMatchRate: { label: 'Keyword Match Rate', orange: 75, red: 55 },
    responsesWithSourcesRate: { label: 'Réponses avec sources', orange: 90, red: 75 },
  };

  const getStatusClass = (value, threshold) => {
    if (value >= threshold.orange) return 'green';
    if (value >= threshold.red) return 'orange';
    return 'red';
  };

  const loadThresholds = () => {
    try {
      const stored = JSON.parse(localStorage.getItem(alertStorageKey) || '{}');
      const merged = {};
      Object.entries(defaultThresholds).forEach(([key, config]) => {
        const src = stored[key] || {};
        let orange = Number(src.orange ?? config.orange);
        let red = Number(src.red ?? config.red);
        orange = Number.isFinite(orange) ? orange : config.orange;
        red = Number.isFinite(red) ? red : config.red;
        if (red >= orange) red = Math.max(0, orange - 5);
        merged[key] = { ...config, orange, red };
      });
      return merged;
    } catch (_error) {
      return { ...defaultThresholds };
    }
  };

  const saveThresholds = (thresholds) => {
    localStorage.setItem(alertStorageKey, JSON.stringify(thresholds));
  };

  let alertThresholds = loadThresholds();

  const statusFromRate = (rate) => {
    if (rate >= 85) return { label: 'Stable', className: 'ok' };
    if (rate >= 65) return { label: 'À surveiller', className: 'warn' };
    return { label: 'Critique', className: 'risk' };
  };

  const renderKpis = (kpis) => {
    if (!governanceKpiGrid) return;
    governanceKpiGrid.innerHTML = '';

    kpis.forEach((kpi) => {
      const card = document.createElement('article');
      card.className = 'governance-kpi-card';
      card.innerHTML = `
        <div class="governance-kpi-label">${kpi.label}</div>
        <div class="governance-kpi-value">${kpi.value}</div>
        <div class="governance-kpi-trend">${kpi.hint}</div>
      `;
      governanceKpiGrid.appendChild(card);
    });
  };

  const ensurePlotly = () => typeof window.Plotly !== 'undefined';

  const renderBarChart = (targetEl, rows, title, color) => {
    if (!targetEl) return;
    if (!ensurePlotly()) {
      targetEl.innerHTML = '<div class="governance-bar-empty">Plotly indisponible.</div>';
      return;
    }

    if (!rows.length) {
      targetEl.innerHTML = '<div class="governance-bar-empty">Aucune donnée disponible.</div>';
      return;
    }

    const labels = rows.map((row) => String(row.label));
    const values = rows.map((row) => Number(row.count || 0));

    window.Plotly.newPlot(
      targetEl,
      [
        {
          type: 'bar',
          orientation: 'h',
          x: values,
          y: labels,
          marker: {
            color,
            line: { color: '#c8d9ef', width: 1 },
          },
          hovertemplate: '%{y}<br>%{x} citations<extra></extra>',
        },
      ],
      {
        margin: { l: 120, r: 20, t: 30, b: 35 },
        title: { text: title, font: { size: 12, color: '#214673' } },
        xaxis: { title: 'Volume', fixedrange: true, gridcolor: '#e8f0fb' },
        yaxis: { autorange: 'reversed', fixedrange: true },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
      },
      { displayModeBar: false, responsive: true },
    );
  };

  const renderUnusedDonut = (targetEl, usedCount, unusedCount) => {
    if (!targetEl) return;
    if (!ensurePlotly()) {
      targetEl.innerHTML = '<div class="governance-bar-empty">Plotly indisponible.</div>';
      return;
    }

    window.Plotly.newPlot(
      targetEl,
      [
        {
          type: 'pie',
          hole: 0.58,
          labels: ['Documents utilisés', 'Documents jamais utilisés'],
          values: [Math.max(usedCount, 0), Math.max(unusedCount, 0)],
          marker: {
            colors: ['#0d6fd6', '#f59e0b'],
          },
          textinfo: 'label+percent',
          hovertemplate: '%{label}<br>%{value}<extra></extra>',
        },
      ],
      {
        margin: { l: 10, r: 10, t: 10, b: 10 },
        paper_bgcolor: 'rgba(0,0,0,0)',
      },
      { displayModeBar: false, responsive: true },
    );
  };

  const renderThresholdControls = (metrics) => {
    if (!governanceThresholds) return;
    governanceThresholds.innerHTML = '';

    Object.entries(alertThresholds).forEach(([key, threshold]) => {
      const row = document.createElement('div');
      row.className = 'governance-threshold-row';
      row.innerHTML = `
        <label>${threshold.label}</label>
        <input type="number" min="0" max="100" step="1" data-kpi="${key}" data-level="orange" value="${threshold.orange}">
        <input type="number" min="0" max="100" step="1" data-kpi="${key}" data-level="red" value="${threshold.red}">
        <span class="governance-threshold-value">${formatPercent(metrics[key] || 0)}</span>
      `;
      governanceThresholds.appendChild(row);
    });

    governanceThresholds.querySelectorAll('input').forEach((input) => {
      input.addEventListener('change', () => {
        const kpi = input.dataset.kpi;
        const level = input.dataset.level;
        if (!kpi || !level || !alertThresholds[kpi]) return;
        const numericValue = Math.max(0, Math.min(100, Number(input.value || 0)));
        alertThresholds[kpi][level] = numericValue;
        if (alertThresholds[kpi].red >= alertThresholds[kpi].orange) {
          alertThresholds[kpi].red = Math.max(0, alertThresholds[kpi].orange - 5);
        }
        saveThresholds(alertThresholds);
        renderAlerting(metrics);
      });
    });
  };

  const renderAlerting = (metrics) => {
    if (!governanceAlertsList || !governanceRecommendations) return;
    governanceAlertsList.innerHTML = '';
    governanceRecommendations.innerHTML = '';

    const statuses = [];
    Object.entries(alertThresholds).forEach(([key, threshold]) => {
      const value = Number(metrics[key] || 0);
      const statusClass = getStatusClass(value, threshold);
      statuses.push({ key, label: threshold.label, value, statusClass });
      const item = document.createElement('div');
      item.className = `governance-alert-item ${statusClass}`;
      item.textContent = `${threshold.label}: ${formatPercent(value)} · Seuils O:${threshold.orange}% R:${threshold.red}%`;
      governanceAlertsList.appendChild(item);
    });

    const recommendations = [];
    const redAlerts = statuses.filter((item) => item.statusClass === 'red');
    const orangeAlerts = statuses.filter((item) => item.statusClass === 'orange');

    if (redAlerts.length) {
      recommendations.push(`Priorité P1: corriger immédiatement ${redAlerts.map((item) => item.label).join(', ')}.`);
      recommendations.push('Activer une revue quotidienne des prompts, retrieval et matching des sources jusqu au retour en zone verte.');
    }
    if (orangeAlerts.length) {
      recommendations.push(`Priorité P2: plan d amélioration ciblé sur ${orangeAlerts.map((item) => item.label).join(', ')}.`);
    }
    if (!redAlerts.length && !orangeAlerts.length) {
      recommendations.push('Tous les KPI surveillés sont en zone verte. Conserver le contrôle hebdomadaire et les tests de non-régression.');
    }
    recommendations.push('Vérifier la qualité des documents jamais utilisés et enrichir le référentiel Databricks pour réduire les angles morts RAG.');

    recommendations.forEach((text) => {
      const li = document.createElement('li');
      li.textContent = text;
      governanceRecommendations.appendChild(li);
    });
  };

  const renderAgentsTable = (agents) => {
    if (!governanceAgentsBody) return;
    governanceAgentsBody.innerHTML = '';

    agents.forEach((agent) => {
      const row = document.createElement('tr');
      row.innerHTML = `
        <td class="governance-agent">${agent.name}</td>
        <td><span class="governance-status-badge ${agent.status.className}">${agent.status.label}</span></td>
        <td>${agent.avgTime}</td>
        <td>${agent.success}</td>
        <td>${agent.errors}</td>
      `;
      governanceAgentsBody.appendChild(row);
    });
  };

  const renderUnusedDocs = (unusedDocuments) => {
    if (!governanceUnusedDocs) return;
    governanceUnusedDocs.innerHTML = '';

    if (!unusedDocuments.length) {
      governanceUnusedDocs.innerHTML = '<li>Toutes les sources du référentiel sont utilisées.</li>';
      return;
    }

    unusedDocuments.slice(0, 6).forEach((documentName) => {
      const li = document.createElement('li');
      li.textContent = documentName;
      governanceUnusedDocs.appendChild(li);
    });
  };

  let governanceContext = {
    retrievalRate: 0,
    sourceMatchRate: 0,
    categoryMatchRate: 0,
    keywordMatchRate: 0,
    withSources: 0,
    topSource: 'Aucune source',
    degradedKpis: [],
    weakAgents: [],
  };

  const localGovernanceAnswer = (question) => {
    const normalized = String(question || '').toLowerCase();
    if (normalized.includes('sources')) {
      return `Les sources les plus utilisées sont dominées par ${governanceContext.topSource}. Le volume de réponses avec sources est actuellement de ${governanceContext.withSources}.`;
    }
    if (normalized.includes('documents')) {
      return `Les documents problématiques sont ceux qui restent non exploités ou faiblement cités. Priorisez leur enrichissement et leur indexation pour réduire les zones aveugles du RAG.`;
    }
    if (normalized.includes('kpi')) {
      if (!governanceContext.degradedKpis.length) {
        return `Les KPI sont globalement stables. Le Retrieval Success Rate est à ${governanceContext.retrievalRate.toFixed(2)}% avec des signaux qualité maîtrisés.`;
      }
      return `Les KPI à surveiller en priorité sont: ${governanceContext.degradedKpis.join(', ')}.`;
    }
    if (normalized.includes('agents') || normalized.includes('agent')) {
      if (!governanceContext.weakAgents.length) {
        return 'Aucun agent critique détecté. Maintenez une surveillance continue des temps de réponse et de la qualité des citations.';
      }
      return `Les agents nécessitant une attention sont: ${governanceContext.weakAgents.join(', ')}.`;
    }
    return `Vue Governance: Retrieval ${governanceContext.retrievalRate.toFixed(2)}%, Source Match ${governanceContext.sourceMatchRate.toFixed(2)}%, Category Match ${governanceContext.categoryMatchRate.toFixed(2)}%, Keyword Match ${governanceContext.keywordMatchRate.toFixed(2)}%.`;
  };

  const mountGovernanceCopilot = () => {
    if (!window.CopilotAssistant?.create) return;
    window.CopilotAssistant.create({
      mode: 'governance',
      questions: [
        'Quelles sources sont les plus utilisées ?',
        'Quels documents posent problème ?',
        'Quels KPI se degradent ?',
        'Quels agents nécessitent une attention ?',
      ],
      initialMessage: 'Sélectionnez une question pour piloter la gouvernance IA bancaire.',
      onAsk: async (question) => {
        try {
          const res = await fetch('/web/governance/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question }),
          });
          if (!res.ok) {
            throw new Error(`HTTP ${res.status}`);
          }
          const payload = await res.json();
          return String(payload.answer || '').trim() || localGovernanceAnswer(question);
        } catch (_error) {
          return localGovernanceAnswer(question);
        }
      },
    });
  };

  const renderFallbackState = () => {
    renderKpis([
      { label: '🛡️ Réponses avec sources', value: 'Indisponible', hint: 'Données non chargées' },
      { label: '📚 Documents cités', value: 'Indisponible', hint: 'Données non chargées' },
      { label: '📈 Retrieval Success Rate', value: 'Indisponible', hint: 'Données non chargées' },
      { label: '✅ Source Match Rate', value: 'Indisponible', hint: 'Données non chargées' },
      { label: '🎯 Category Match Rate', value: 'Indisponible', hint: 'Données non chargées' },
      { label: '🧠 Keyword Match Rate', value: 'Indisponible', hint: 'Données non chargées' },
    ]);
    renderBarChart(governanceTopSourcesChart, [], 'Sources', '#0d6fd6');
    renderBarChart(governanceTopDocumentsChart, [], 'Documents', '#0f9fbd');
    renderUnusedDonut(governanceUnusedDocumentsChart, 0, 0);
    renderUnusedDocs([]);
  };

  try {
    const [governanceResponse, evaluationResponse, documentQualityResponse] = await Promise.all([
      fetch('/governance'),
      fetch('/evaluation'),
      fetch('/web/governance/document-quality'),
    ]);

    if (!governanceResponse.ok) {
      throw new Error(`HTTP ${governanceResponse.status}`);
    }

    const governanceData = await governanceResponse.json();
    const evaluationData = evaluationResponse.ok ? await evaluationResponse.json() : {};
    const documentQuality = documentQualityResponse.ok ? await documentQualityResponse.json() : {};

    const retrievalSuccessRate = Number(governanceData.retrieval_success_rate || 0);
    const responsesWithSources = Number(governanceData.responses_with_sources || 0);
    const responsesWithoutSources = Number(governanceData.responses_without_sources || 0);
    const totalResponses = Math.max(responsesWithSources + responsesWithoutSources, 1);
    const citations = Array.isArray(governanceData.citations_per_source) ? governanceData.citations_per_source : [];

    const sourceMatchRate = Number(evaluationData.source_match_rate || 0);
    const categoryMatchRate = Number(evaluationData.category_match_rate || 0);
    const keywordMatchRate = Number(evaluationData.keyword_match_rate || 0);
    const avgResponseTime = Number(evaluationData.avg_response_time || 0);

    const degradedKpis = [];
    if (retrievalSuccessRate < 85) degradedKpis.push('Retrieval Success Rate');
    if (sourceMatchRate < 80) degradedKpis.push('Source Match Rate');
    if (categoryMatchRate < 80) degradedKpis.push('Category Match Rate');
    if (keywordMatchRate < 75) degradedKpis.push('Keyword Match Rate');

    const kpis = [
      {
        label: '🛡️ Réponses avec sources',
        value: formatInteger(responsesWithSources),
        hint: `${formatPercent((responsesWithSources / totalResponses) * 100)} des réponses`,
      },
      {
        label: '📚 Documents cités',
        value: formatInteger(citations.reduce((sum, item) => sum + Number(item.count || 0), 0)),
        hint: `${formatInteger(citations.length)} sources distinctes`,
      },
      {
        label: '📈 Retrieval Success Rate',
        value: formatPercent(retrievalSuccessRate),
        hint: `${formatPercent(governanceData.retrieval_empty_rate || 0)} retrieval vide`,
      },
      {
        label: '✅ Source Match Rate',
        value: formatPercent(sourceMatchRate),
        hint: 'Alignement réponse vs source',
      },
      {
        label: '🎯 Category Match Rate',
        value: formatPercent(categoryMatchRate),
        hint: 'Précision de classification métier',
      },
      {
        label: '🧠 Keyword Match Rate',
        value: formatPercent(keywordMatchRate),
        hint: 'Couverture des termes critiques',
      },
    ];
    renderKpis(kpis);

    const topSourcesRows = (Array.isArray(documentQuality.top_sources) ? documentQuality.top_sources : citations)
      .slice(0, 6)
      .map((item) => ({
      label: String(item.source || 'Source inconnue'),
      count: Number(item.count || 0),
      }));
    renderBarChart(governanceTopSourcesChart, topSourcesRows, 'Top Sources', '#0c67d6');

    const topDocumentsRows = (Array.isArray(documentQuality.top_documents) ? documentQuality.top_documents : citations)
      .slice(0, 6)
      .map((item) => ({
      label: `Doc · ${String(item.source || 'Inconnu')}`,
      count: Number(item.count || 0),
      }));
    renderBarChart(governanceTopDocumentsChart, topDocumentsRows, 'Top Documents', '#0fa6ba');

    const neverUsedDocs = Array.isArray(documentQuality.unused_documents) ? documentQuality.unused_documents : [];
    const referentialCount = Number(documentQuality.referential_count || 0);
    const usedCount = Math.max(referentialCount - neverUsedDocs.length, 0);
    renderUnusedDonut(governanceUnusedDocumentsChart, usedCount, neverUsedDocs.length);
    renderUnusedDocs(neverUsedDocs);

    const retrievalStatus = statusFromRate(retrievalSuccessRate);
    const analyticsStatus = statusFromRate(keywordMatchRate || 0);
    const governanceStatus = statusFromRate(sourceMatchRate || 0);
    const evaluationStatus = statusFromRate(categoryMatchRate || 0);
    const complianceStatus = statusFromRate(Math.min(sourceMatchRate || 0, retrievalSuccessRate || 0));

    const agentRows = [
      {
        name: 'Retrieval Agent',
        status: retrievalStatus,
        avgTime: formatMs(avgResponseTime * 0.6),
        success: formatPercent(retrievalSuccessRate),
        errors: formatPercent(100 - retrievalSuccessRate),
      },
      {
        name: 'Analytics Agent',
        status: analyticsStatus,
        avgTime: formatMs(avgResponseTime * 1.1),
        success: formatPercent(keywordMatchRate),
        errors: formatPercent(100 - keywordMatchRate),
      },
      {
        name: 'Governance Agent',
        status: governanceStatus,
        avgTime: formatMs(avgResponseTime * 1.25),
        success: formatPercent(sourceMatchRate),
        errors: formatPercent(100 - sourceMatchRate),
      },
      {
        name: 'Evaluation Agent',
        status: evaluationStatus,
        avgTime: formatMs(avgResponseTime || governanceData.avg_context_chars || 0),
        success: formatPercent(categoryMatchRate),
        errors: formatPercent(100 - categoryMatchRate),
      },
      {
        name: 'Compliance Agent',
        status: complianceStatus,
        avgTime: formatMs(avgResponseTime * 1.35),
        success: formatPercent(Math.min(sourceMatchRate || 0, retrievalSuccessRate || 0)),
        errors: formatPercent(100 - Math.min(sourceMatchRate || 0, retrievalSuccessRate || 0)),
      },
    ];
    renderAgentsTable(agentRows);

    governanceContext = {
      retrievalRate: retrievalSuccessRate,
      sourceMatchRate,
      categoryMatchRate,
      keywordMatchRate,
      withSources: responsesWithSources,
      topSource: citations[0]?.source || 'Aucune source',
      degradedKpis,
      weakAgents: agentRows.filter((agent) => agent.status.className !== 'ok').map((agent) => agent.name),
    };

    const monitoredMetrics = {
      retrievalSuccessRate,
      sourceMatchRate,
      categoryMatchRate,
      keywordMatchRate,
      responsesWithSourcesRate: (responsesWithSources / totalResponses) * 100,
    };

    renderThresholdControls(monitoredMetrics);
    renderAlerting(monitoredMetrics);

    if (governanceResetThresholds) {
      governanceResetThresholds.onclick = () => {
        alertThresholds = loadThresholds();
        Object.keys(alertThresholds).forEach((key) => {
          alertThresholds[key].orange = defaultThresholds[key].orange;
          alertThresholds[key].red = defaultThresholds[key].red;
        });
        saveThresholds(alertThresholds);
        renderThresholdControls(monitoredMetrics);
        renderAlerting(monitoredMetrics);
      };
    }

    mountGovernanceCopilot();
  } catch (error) {
    renderFallbackState();
    if (governanceAgentsBody) {
      governanceAgentsBody.innerHTML = '<tr><td colspan="5">Monitoring indisponible</td></tr>';
    }
    if (governanceAlertsList) {
      governanceAlertsList.innerHTML = '<div class="governance-alert-item red">Impossible de calculer les alertes.</div>';
    }
    if (governanceRecommendations) {
      governanceRecommendations.innerHTML = '<li>Vérifier la disponibilité des endpoints /governance, /evaluation et /web/governance/document-quality.</li>';
    }
    mountGovernanceCopilot();
  }
});
