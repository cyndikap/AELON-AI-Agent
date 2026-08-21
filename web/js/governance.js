document.addEventListener('DOMContentLoaded', async () => {
  const governanceKpiGrid = document.getElementById('governanceKpiGrid');
  const governanceAgentsBody = document.getElementById('governanceAgentsBody');
  const governanceTopSources = document.getElementById('governanceTopSources');
  const governanceTopDocuments = document.getElementById('governanceTopDocuments');
  const governanceUnusedDocs = document.getElementById('governanceUnusedDocs');

  const formatPercent = (value) => `${Number(value || 0).toFixed(2)}%`;
  const formatInteger = (value) => String(Math.round(Number(value || 0)));
  const formatMs = (value) => `${Math.round(Number(value || 0))} ms`;

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

  const renderBarRows = (container, rows) => {
    if (!container) return;
    container.innerHTML = '';

    if (!rows.length) {
      container.innerHTML = '<div class="governance-bar-empty">Aucune donnée disponible.</div>';
      return;
    }

    const maxValue = Math.max(...rows.map((row) => Number(row.count || 0)), 1);
    rows.forEach((row) => {
      const width = Math.max((Number(row.count || 0) / maxValue) * 100, 4);
      const item = document.createElement('div');
      item.className = 'governance-bar-row';
      item.innerHTML = `
        <div class="governance-bar-label">${row.label}</div>
        <div class="governance-bar-track"><div class="governance-bar-fill" style="width:${width}%"></div></div>
        <div class="governance-bar-value">${formatInteger(row.count)}</div>
      `;
      container.appendChild(item);
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
    renderBarRows(governanceTopSources, []);
    renderBarRows(governanceTopDocuments, []);
    renderUnusedDocs([]);
  };

  try {
    const [governanceResponse, evaluationResponse] = await Promise.all([
      fetch('/governance'),
      fetch('/evaluation'),
    ]);

    if (!governanceResponse.ok) {
      throw new Error(`HTTP ${governanceResponse.status}`);
    }

    const governanceData = await governanceResponse.json();
    const evaluationData = evaluationResponse.ok ? await evaluationResponse.json() : {};

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

    const topSourcesRows = citations.slice(0, 6).map((item) => ({
      label: String(item.source || 'Source inconnue'),
      count: Number(item.count || 0),
    }));
    renderBarRows(governanceTopSources, topSourcesRows);

    const topDocumentsRows = citations.slice(0, 6).map((item) => ({
      label: `Doc · ${String(item.source || 'Inconnu')}`,
      count: Number(item.count || 0),
    }));
    renderBarRows(governanceTopDocuments, topDocumentsRows);

    const governanceReferential = [
      'RGPD_Guide_Interne.pdf',
      'DORA_Controls_2026.pdf',
      'KYC_Operating_Standard.pdf',
      'Politique_AntiFraude.pdf',
      'Base_ACPR_Conformite.pdf',
      'Procedure_Gestion_Reclamations.pdf',
      'SLA_Contact_Center.pdf',
      'Nomenclature_Categories_Client.pdf',
    ];
    const usedSources = new Set(citations.map((item) => String(item.source || '').trim().toLowerCase()).filter(Boolean));
    const neverUsedDocs = governanceReferential.filter((name) => !usedSources.has(name.toLowerCase()));
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

    mountGovernanceCopilot();
  } catch (error) {
    renderFallbackState();
    if (governanceAgentsBody) {
      governanceAgentsBody.innerHTML = '<tr><td colspan="5">Monitoring indisponible</td></tr>';
    }
    mountGovernanceCopilot();
  }
});
