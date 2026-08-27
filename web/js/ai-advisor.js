document.addEventListener('DOMContentLoaded', async () => {
  const executiveListEl = document.getElementById('advisorExecutiveList');
  const priorityEl = document.getElementById('advisorPriority');
  const strengthsEl = document.getElementById('advisorStrengths');
  const improvementsEl = document.getElementById('advisorImprovements');
  const recommendationsEl = document.getElementById('advisorRecommendations');
  const faqCardsEl = document.getElementById('advisorFaqCards');
  const alertCriticalEl = document.getElementById('advisorAlertCritical');
  const alertWatchEl = document.getElementById('advisorAlertWatch');
  const alertOkEl = document.getElementById('advisorAlertOk');

  const chatHistoryEl = document.getElementById('advisorChatHistory');
  const chatFormEl = document.getElementById('advisorChatForm');
  const chatInputEl = document.getElementById('advisorChatInput');
  const chatSendEl = document.getElementById('advisorChatSend');

  const chatTurns = [];
  let lastSnapshot = null;
  let busy = false;

  const FAQ_QUESTIONS = [
    'Pourquoi ce score est-il faible ?',
    'Que faut-il ameliorer ?',
    'Le systeme est-il pret pour la production ?',
    'Quels sont les principaux risques ?',
    'Quelles categories sont les moins performantes ?',
  ];

  const safeNum = (value, defaultValue = 0) => {
    const n = Number(value);
    return Number.isFinite(n) ? n : defaultValue;
  };

  const asPercent = (value) => `${safeNum(value).toFixed(0)} %`;

  const aggregateCounts = (rows, key, fallback = 'autre') => {
    const map = new Map();
    (Array.isArray(rows) ? rows : []).forEach((row) => {
      const label = String(row?.[key] || fallback).trim() || fallback;
      map.set(label, (map.get(label) || 0) + 1);
    });
    return [...map.entries()]
      .map(([label, count]) => ({ label, count }))
      .sort((a, b) => b.count - a.count);
  };

  const scoreStatus = (value, thresholds = { ok: 85, watch: 65 }) => {
    if (value >= thresholds.ok) return 'ok';
    if (value >= thresholds.watch) return 'watch';
    return 'critical';
  };

  const buildSnapshot = (analytics, governance, evaluation, rows) => {
    const categories = aggregateCounts(rows, 'category', 'autre');
    const categoryTop = categories.slice(0, 3);
    const weakestCategory = categoryTop.length ? categoryTop[0].label : 'N/A';

    const retrievalRate = safeNum(governance.retrieval_success_rate);
    const sourceMatchRate = safeNum(evaluation.source_match_rate);
    const categoryMatchRate = safeNum(evaluation.category_match_rate);
    const keywordMatchRate = safeNum(evaluation.keyword_match_rate);
    const responseTimeMs = safeNum(evaluation.avg_response_time || analytics.avg_response_time_ms);
    const coverageRate = safeNum(evaluation.category_coverage);

    const metrics = [
      {
        key: 'retrieval',
        label: 'Retrieval Success Rate',
        value: retrievalRate,
        format: asPercent(retrievalRate),
        status: scoreStatus(retrievalRate, { ok: 90, watch: 75 }),
        impact: 'Un retrieval faible augmente le risque de reponses inexactes.',
      },
      {
        key: 'source_match',
        label: 'Source Match Rate',
        value: sourceMatchRate,
        format: asPercent(sourceMatchRate),
        status: scoreStatus(sourceMatchRate, { ok: 90, watch: 75 }),
        impact: 'Un faible alignement source degrade la confiance metier.',
      },
      {
        key: 'category_match',
        label: 'Category Match Rate',
        value: categoryMatchRate,
        format: asPercent(categoryMatchRate),
        status: scoreStatus(categoryMatchRate, { ok: 85, watch: 65 }),
        impact: 'Des erreurs de categorisation peuvent orienter vers des actions inadaptées.',
      },
      {
        key: 'keyword_match',
        label: 'Keyword Match Rate',
        value: keywordMatchRate,
        format: asPercent(keywordMatchRate),
        status: scoreStatus(keywordMatchRate, { ok: 85, watch: 65 }),
        impact: 'Une precision semantique insuffisante nuit a la pertinence metier.',
      },
      {
        key: 'latency',
        label: 'Temps moyen de reponse',
        value: responseTimeMs,
        format: `${Math.round(responseTimeMs)} ms`,
        status: responseTimeMs <= 4500 ? 'ok' : responseTimeMs <= 12000 ? 'watch' : 'critical',
        impact: 'Une latence elevee degrade l experience utilisateur et augmente les escalades.',
      },
      {
        key: 'coverage',
        label: 'Couverture metier',
        value: coverageRate,
        format: asPercent(coverageRate),
        status: scoreStatus(coverageRate, { ok: 80, watch: 60 }),
        impact: 'Une couverture trop faible expose des cas metier non traites.',
      },
    ];

    const strengths = metrics.filter((m) => m.status === 'ok');
    const improvements = metrics.filter((m) => m.status !== 'ok');

    const priority = improvements.find((m) => m.status === 'critical') || improvements[0] || null;

    return {
      metrics,
      strengths,
      improvements,
      priority,
      categories,
      categoryTop,
      weakestCategory,
      retrievalRate,
      sourceMatchRate,
      categoryMatchRate,
      keywordMatchRate,
      responseTimeMs,
      coverageRate,
      totalConversations: safeNum(analytics.total_conversations || rows.length),
    };
  };

  const renderExecutive = (snapshot) => {
    if (!executiveListEl || !priorityEl) return;

    const lines = [];
    if (snapshot.retrievalRate >= 90) lines.push('✅ Retrieval documentaire excellent');
    if (snapshot.sourceMatchRate >= 90) lines.push('✅ Sources correctement utilisees');
    if (snapshot.categoryMatchRate < 85) lines.push(`⚠ Category Match Rate a surveiller (${asPercent(snapshot.categoryMatchRate)})`);
    if (snapshot.responseTimeMs > 4500) lines.push(`⚠ Temps de reponse superieur a l objectif (${Math.round(snapshot.responseTimeMs)} ms)`);
    if (!lines.length) lines.push('✅ Les indicateurs cles sont globalement conformes.');

    executiveListEl.innerHTML = lines.map((line) => `<li>${line}</li>`).join('');

    if (snapshot.priority) {
      priorityEl.textContent = `🎯 Priorite principale: Ameliorer ${snapshot.priority.label.toLowerCase()}.`;
    } else {
      priorityEl.textContent = '🎯 Priorite principale: maintenir la stabilite actuelle et surveiller les signaux faibles.';
    }
  };

  const renderStrengths = (snapshot) => {
    if (!strengthsEl) return;
    if (!snapshot.strengths.length) {
      strengthsEl.innerHTML = '<li>Aucun KPI en zone excellente actuellement.</li>';
      return;
    }

    strengthsEl.innerHTML = snapshot.strengths
      .map((metric) => `<li><strong>${metric.label}</strong>: ${metric.format}</li>`)
      .join('');
  };

  const renderImprovements = (snapshot) => {
    if (!improvementsEl) return;
    if (!snapshot.improvements.length) {
      improvementsEl.innerHTML = '<div class="advisor-improvement-card"><h4>Situation stable</h4><p>Aucun point critique detecte sur les KPI suivis.</p></div>';
      return;
    }

    improvementsEl.innerHTML = snapshot.improvements
      .map((metric) => {
        const icon = metric.status === 'critical' ? '🔴' : '🟠';
        return `
          <article class="advisor-improvement-card">
            <h4>${icon} ${metric.label}: ${metric.format}</h4>
            <p><strong>Impact:</strong> ${metric.impact}</p>
          </article>
        `;
      })
      .join('');
  };

  const renderRecommendations = (snapshot) => {
    if (!recommendationsEl) return;

    const recommendations = [];

    if (snapshot.categoryMatchRate < 85) {
      recommendations.push('🎯 Recommandation 1: Ameliorer les exemples d entrainement sur les categories Fraude et Carte bancaire pour reduire les erreurs de classement.');
    }
    if (snapshot.responseTimeMs > 4500) {
      recommendations.push('🎯 Recommandation 2: Reduire les appels LLM redondants et optimiser les parcours les plus frequents pour baisser la latence.');
    }
    if (snapshot.sourceMatchRate < 90 || snapshot.coverageRate < 80) {
      recommendations.push('🎯 Recommandation 3: Enrichir les documents RGPD et KYC, puis renforcer leur priorisation dans le retrieval.');
    }
    if (snapshot.keywordMatchRate < 85) {
      recommendations.push('🎯 Recommandation 4: Renforcer les formulations metier cibles pour augmenter la precision des reponses.');
    }

    if (!recommendations.length) {
      recommendations.push('🎯 Continuer le suivi hebdomadaire et lancer des tests de non-regression pour conserver le niveau actuel.');
    }

    recommendationsEl.innerHTML = recommendations.map((line) => `<li>${line}</li>`).join('');
  };

  const renderAlerts = (snapshot) => {
    if (!alertCriticalEl || !alertWatchEl || !alertOkEl) return;

    const critical = [];
    const watch = [];
    const ok = [];

    snapshot.metrics.forEach((metric) => {
      const line = `${metric.label} (${metric.format})`;
      if (metric.status === 'critical') critical.push(line);
      else if (metric.status === 'watch') watch.push(line);
      else ok.push(line);
    });

    alertCriticalEl.innerHTML = (critical.length ? critical : ['Aucune alerte critique']).map((line) => `<li>${line}</li>`).join('');
    alertWatchEl.innerHTML = (watch.length ? watch : ['Aucun point a surveiller']).map((line) => `<li>${line}</li>`).join('');
    alertOkEl.innerHTML = (ok.length ? ok : ['Aucun KPI conforme']).map((line) => `<li>${line}</li>`).join('');
  };

  const addChatTurn = (role, text, options = {}) => {
    if (!chatHistoryEl) return null;
    const row = document.createElement('div');
    row.className = `advisor-chat-row ${role}${options.typing ? ' typing' : ''}`;
    const bubble = document.createElement('div');
    bubble.className = 'advisor-chat-bubble';
    bubble.textContent = options.typing ? 'Analyse en cours...' : String(text || '').trim();
    row.appendChild(bubble);
    chatHistoryEl.appendChild(row);
    chatHistoryEl.scrollTop = chatHistoryEl.scrollHeight;
    return row;
  };

  const setChatBusy = (value) => {
    busy = value;
    if (chatInputEl) chatInputEl.disabled = value;
    if (chatSendEl) chatSendEl.disabled = value;
    if (!faqCardsEl) return;
    faqCardsEl.querySelectorAll('button').forEach((button) => {
      button.disabled = value;
    });
  };

  const answerFromSnapshot = (question, history) => {
    const q = String(question || '').toLowerCase();
    const s = lastSnapshot;
    if (!s) return 'Les donnees AI Advisor ne sont pas encore disponibles.';

    if (q.includes('pourquoi') && q.includes('category')) {
      return `Le Category Match Rate est a ${asPercent(s.categoryMatchRate)}. Les demandes hybrides (fraude, carte, virement) sont parfois classees dans une categorie voisine, ce qui impacte le score.`;
    }
    if (q.includes('kpi') || q.includes('attention')) {
      const risks = s.improvements.map((m) => `${m.label} (${m.format})`);
      if (!risks.length) return 'Aucun KPI critique ou sensible detecte actuellement. Le systeme est globalement stable.';
      return `Les KPI a prioriser sont: ${risks.join(', ')}.`;
    }
    if (q.includes('recommand')) {
      return 'Priorites recommandees: 1) renforcer les exemples de categorisation metier, 2) optimiser les appels LLM pour la latence, 3) enrichir les documents RGPD/KYC peu exploitables.';
    }
    if (q.includes('retrieval')) {
      return `Le Retrieval Success Rate est a ${asPercent(s.retrievalRate)}. Pour progresser: enrichir le corpus sur les cas ambigus, revoir le chunking des documents longs et resserrer les regles de ranking.`;
    }
    if (q.includes('temps de reponse') || q.includes('latence')) {
      return `Le temps moyen actuel est ${Math.round(s.responseTimeMs)} ms. La latence provient surtout des parcours multi-etapes: il faut reduire les appels redondants et precharger les contextes frequents.`;
    }
    if (q.includes('production') || q.includes('deploiement')) {
      const criticalCount = s.metrics.filter((m) => m.status === 'critical').length;
      if (criticalCount === 0) {
        return 'Le systeme est proche d un niveau production, sous reserve de maintenir les tests de non-regression et la surveillance continue des KPI sensibles.';
      }
      return `Le systeme n est pas encore totalement pret pour un deploiement large: ${criticalCount} indicateur(s) critique(s) restent a corriger avant generalisation.`;
    }
    if (q.includes('categories') && q.includes('moins')) {
      const top = s.categoryTop.map((c) => `${c.label} (${c.count})`).join(', ');
      return `Categories dominantes observees: ${top}. Les categories les moins performantes a investiguer sont celles qui se retrouvent souvent dans "autre".`;
    }

    const lastAssistant = [...history].reverse().find((turn) => turn.role === 'assistant')?.content;
    if (lastAssistant && (q.includes('exemple') || q.includes('precis') || q.includes('detail'))) {
      return `Exemple concret: ${lastAssistant} Sur un cas "fraude" ambigu, un mauvais classement de categorie peut orienter vers une reponse carte standard au lieu d un protocole de securite.`;
    }

    return `Vue globale AI Advisor: retrieval ${asPercent(s.retrievalRate)}, source match ${asPercent(s.sourceMatchRate)}, category match ${asPercent(s.categoryMatchRate)}, latence ${Math.round(s.responseTimeMs)} ms. La priorite est d ameliorer la categorisation et la precision metier.`;
  };

  const askAdvisor = async (question) => {
    const userText = String(question || '').trim();
    if (!userText || busy) return;

    addChatTurn('user', userText);
    chatTurns.push({ role: 'user', content: userText });
    if (chatInputEl) chatInputEl.value = '';

    setChatBusy(true);
    const typingRow = addChatTurn('assistant', '', { typing: true });

    try {
      const answer = answerFromSnapshot(userText, chatTurns);
      if (typingRow) typingRow.remove();
      addChatTurn('assistant', answer);
      chatTurns.push({ role: 'assistant', content: answer });
    } catch (_error) {
      if (typingRow) typingRow.remove();
      const fallback = 'Je ne peux pas finaliser l analyse pour le moment. Merci de reessayer dans quelques instants.';
      addChatTurn('assistant', fallback);
      chatTurns.push({ role: 'assistant', content: fallback });
    } finally {
      setChatBusy(false);
      if (chatInputEl) chatInputEl.focus();
    }
  };

  const renderFaq = () => {
    if (!faqCardsEl) return;
    faqCardsEl.innerHTML = '';
    FAQ_QUESTIONS.forEach((question) => {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'advisor-faq-card';
      button.textContent = question;
      button.addEventListener('click', () => {
        askAdvisor(question);
      });
      faqCardsEl.appendChild(button);
    });
  };

  const renderEmptyState = () => {
    if (executiveListEl) executiveListEl.innerHTML = '<li>⚠ Donnees indisponibles temporairement.</li>';
    if (priorityEl) priorityEl.textContent = '🎯 Priorite principale: verifier la disponibilite des endpoints analytics/governance/evaluation.';
    if (strengthsEl) strengthsEl.innerHTML = '<li>Pas de lecture fiable actuellement.</li>';
    if (improvementsEl) improvementsEl.innerHTML = '<div class="advisor-improvement-card"><h4>Indisponible</h4><p>Impossible de charger l analyse automatique pour le moment.</p></div>';
    if (recommendationsEl) recommendationsEl.innerHTML = '<li>Relancer les services de donnees et reexecuter l analyse.</li>';
    if (alertCriticalEl) alertCriticalEl.innerHTML = '<li>Donnees non disponibles</li>';
    if (alertWatchEl) alertWatchEl.innerHTML = '<li>Donnees non disponibles</li>';
    if (alertOkEl) alertOkEl.innerHTML = '<li>Donnees non disponibles</li>';
  };

  if (chatFormEl && chatInputEl) {
    chatFormEl.addEventListener('submit', (event) => {
      event.preventDefault();
      askAdvisor(chatInputEl.value);
    });
  }

  renderFaq();
  addChatTurn('assistant', 'Je suis AI Advisor. Je synthétise vos KPI et je vous propose les meilleures actions a engager.');
  chatTurns.push({
    role: 'assistant',
    content: 'Je suis AI Advisor. Je synthétise vos KPI et je vous propose les meilleures actions a engager.',
  });

  try {
    const [analyticsRes, governanceRes, evaluationRes, rowsRes] = await Promise.all([
      fetch('/analytics'),
      fetch('/governance'),
      fetch('/evaluation'),
      fetch('/web/analytics/data'),
    ]);

    if (!analyticsRes.ok || !governanceRes.ok || !evaluationRes.ok || !rowsRes.ok) {
      throw new Error('fetch failure');
    }

    const analytics = await analyticsRes.json();
    const governance = await governanceRes.json();
    const evaluation = await evaluationRes.json();
    const rowsPayload = await rowsRes.json();
    const rows = Array.isArray(rowsPayload.rows) ? rowsPayload.rows : [];

    lastSnapshot = buildSnapshot(analytics, governance, evaluation, rows);

    renderExecutive(lastSnapshot);
    renderStrengths(lastSnapshot);
    renderImprovements(lastSnapshot);
    renderRecommendations(lastSnapshot);
    renderAlerts(lastSnapshot);
  } catch (_error) {
    renderEmptyState();
  }
});
