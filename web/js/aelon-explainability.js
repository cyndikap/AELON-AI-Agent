(function () {
  const modalId = 'aelonKpiExplainModal';

  function toNumber(value) {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : null;
  }

  function computeStatus(score) {
    if (!Number.isFinite(score)) {
      return { icon: 'ℹ️', label: 'Information', className: 'info' };
    }
    if (score >= 85) {
      return { icon: '✅', label: 'Excellent', className: 'excellent' };
    }
    if (score >= 65) {
      return { icon: '⚠️', label: 'À surveiller', className: 'warning' };
    }
    return { icon: '❌', label: 'Critique', className: 'critical' };
  }

  function safeText(value, fallback) {
    const text = String(value || '').trim();
    return text || fallback;
  }

  function statusBusinessLabel(status) {
    if (!status || !status.className) return 'à interpréter';
    if (status.className === 'excellent') return 'bonne';
    if (status.className === 'warning') return 'à surveiller';
    if (status.className === 'critical') return 'insuffisante';
    return 'à interpréter';
  }

  function buildDefaultImpact(title) {
    const label = String(title || '').toLowerCase();
    if (label.includes('latence') || label.includes('response time')) {
      return [
        'Expérience client plus fluide',
        'Réduction du temps d attente',
        'Diminution des escalades liées à l impatience',
      ];
    }
    if (label.includes('category') || label.includes('catégorie') || label.includes('categorie')) {
      return [
        'Meilleure orientation des demandes client',
        'Actions métier plus ciblées',
        'Réduction des erreurs de traitement',
      ];
    }
    if (label.includes('source')) {
      return [
        'Réponses plus fiables',
        'Meilleure traçabilité',
        'Réduction du risque d erreur',
      ];
    }
    return [
      'Vision plus claire de la performance',
      'Décisions métier plus rapides',
      'Pilotage plus fiable de la qualité',
    ];
  }

  function buildEnterpriseImpact(title) {
    const label = String(title || '').toLowerCase();
    if (label.includes('latence') || label.includes('response time') || label.includes('temps')) {
      return [
        'Ameliore la productivite du service client',
        'Reduit les couts de traitement des demandes',
        'Limite le risque d insatisfaction sur les parcours urgents',
      ];
    }
    if (label.includes('fraude') || label.includes('fraud')) {
      return [
        'Renforce la prevention des incidents de securite',
        'Protege la confiance client',
        'Contribue a la maitrise du risque operationnel',
      ];
    }
    if (label.includes('category') || label.includes('catégorie') || label.includes('categorie')) {
      return [
        'Ameliore le routage des dossiers',
        'Evite des actions inadaptées',
        'Accélère la prise de décision métier',
      ];
    }
    return [
      'Renforce la fiabilite du service rendu',
      'Facilite la justification des decisions',
      'Consolide la qualite percue de la plateforme',
    ];
  }

  function semanticKey(title) {
    const label = String(title || '').toLowerCase();
    if (label.includes('source')) return 'source';
    if (label.includes('retrieval') || label.includes('document')) return 'retrieval';
    if (label.includes('category') || label.includes('catégorie') || label.includes('categorie')) return 'category';
    if (label.includes('keyword') || label.includes('precision')) return 'keyword';
    if (label.includes('latence') || label.includes('response time') || label.includes('temps')) return 'latency';
    if (label.includes('fraude') || label.includes('fraud')) return 'fraud';
    return 'generic';
  }

  function bankingExampleByKey(key) {
    const examples = {
      source: {
        question: 'Comment faire opposition a ma carte bancaire ?',
        expected: 'Guide opposition carte, procedure securite bancaire',
        used: 'Guide opposition carte, procedure securite bancaire',
        result: '✅ Les informations utilisees correspondent au besoin client.',
      },
      retrieval: {
        question: 'Comment realiser un virement vers un nouveau beneficiaire ?',
        expected: 'Procedure virement, verification beneficiaire, delais',
        used: 'Procedure virement, verification beneficiaire, delais',
        result: '✅ AELON retrouve les bons contenus pour repondre sans ambiguite.',
      },
      category: {
        question: 'Je ne peux plus acceder a mon espace bancaire en ligne.',
        expected: 'Categorie acces compte',
        used: 'Categorie acces compte',
        result: '✅ La demande est bien comprise et orientee vers le bon traitement.',
      },
      keyword: {
        question: 'Quels sont mes droits sur mes donnees personnelles ?',
        expected: 'Droits RGPD, suppression, rectification, opposition',
        used: 'Droits RGPD, suppression, rectification, opposition',
        result: '✅ Les elements metier essentiels sont bien couverts dans la reponse.',
      },
      latency: {
        question: 'Ma carte est bloquee, que faire tout de suite ?',
        expected: 'Etapes immediates, contact support, securisation',
        used: 'Etapes immediates, contact support, securisation',
        result: '✅ Reponse rapide permettant une action immediate du client.',
      },
      fraud: {
        question: 'Je constate un paiement inconnu sur mon compte.',
        expected: 'Signalement fraude, blocage carte, verification operations',
        used: 'Signalement fraude, blocage carte, verification operations',
        result: '✅ Le parcours de vigilance est correctement active.',
      },
      generic: {
        question: 'Comment contacter un conseiller bancaire ?',
        expected: 'Canaux de contact, horaires, niveau de priorite',
        used: 'Canaux de contact, horaires, niveau de priorite',
        result: '✅ Reponse claire et exploitable pour l utilisateur.',
      },
    };
    return examples[key] || examples.generic;
  }

  function toBusinessTitle(title) {
    const key = semanticKey(title);
    const mapping = {
      source: 'Fiabilite des informations utilisees',
      retrieval: 'Qualite des informations retrouvees',
      category: 'Compréhension des demandes clients',
      keyword: 'Precision des reponses metier',
      latency: 'Rapidite de traitement',
      fraud: 'Vigilance sur les situations sensibles',
      generic: safeText(title, 'Indicateur metier AELON'),
    };
    return mapping[key] || safeText(title, 'Indicateur metier AELON');
  }

  function humanTemplate(title) {
    const key = semanticKey(title);
    const templates = {
      source: {
        oneLiner: 'Cet indicateur mesure si AELON s appuie sur les bons documents pour construire ses reponses.',
        importance: 'Quand AELON utilise les bonnes sources, la reponse est plus fiable, plus claire et plus facile a justifier.',
        recommendationHigh: 'Indicateur satisfaisant. Continuez a enrichir la documentation et a maintenir la qualite des sources.',
        recommendationLow: 'Priorisez la revue des sources de reference pour fiabiliser les reponses sur les sujets sensibles.',
        aiAnalysis: '🤖 Analyse AELON: les reponses s appuient globalement sur des informations coherentes. Ce point renforce la confiance des equipes metier.',
      },
      retrieval: {
        oneLiner: 'Cet indicateur montre si AELON retrouve les bons contenus avant de rediger une reponse.',
        importance: 'Si AELON ne retrouve pas les bonnes informations, la reponse finale risque d etre inexacte.',
        recommendationHigh: 'Le niveau est solide. Continuez a faire vivre le corpus avec les nouveaux cas metier.',
        recommendationLow: 'Renforcez les contenus sur les themes en echec recurrent et clarifiez les documents de reference.',
        aiAnalysis: '🤖 Analyse AELON: la qualite des informations retrouvees conditionne directement la qualite des reponses clients.',
      },
      category: {
        oneLiner: 'Cet indicateur verifie si AELON comprend correctement le sujet metier de la demande client.',
        importance: 'Une mauvaise comprehension du sujet peut orienter vers une reponse incomplete ou hors contexte.',
        recommendationHigh: 'Bonne maitrise du classement metier. Maintenez la taxonomie et les exemples actuels.',
        recommendationLow: 'Renforcez les exemples metier et clarifiez les categories proches pour limiter les confusions.',
        aiAnalysis: '🤖 Analyse AELON: la bonne comprehension des demandes permet d orienter plus vite vers la bonne action.',
      },
      keyword: {
        oneLiner: 'Cet indicateur mesure la precision des reponses sur les points metier importants attendus.',
        importance: 'Une reponse qui oublie les elements essentiels peut etre correcte en apparence mais insuffisante en pratique.',
        recommendationHigh: 'Le niveau de precision est bon. Conservez ce standard sur les parcours sensibles.',
        recommendationLow: 'Travaillez la formulation des reponses et la couverture des cas metier avec des exemples concrets.',
        aiAnalysis: '🤖 Analyse AELON: cet indicateur montre si les reponses couvrent vraiment les attentes metier de l utilisateur.',
      },
      latency: {
        oneLiner: 'Cet indicateur mesure la rapidite de reponse d AELON pour l utilisateur.',
        importance: 'Une bonne rapidite ameliore l experience client et limite les abandons de parcours.',
        recommendationHigh: 'Le delai est satisfaisant. Surveillez la stabilite lors des pics de charge.',
        recommendationLow: 'Priorisez l optimisation des parcours les plus frequents pour reduire l attente percue.',
        aiAnalysis: '🤖 Analyse AELON: la rapidite de traitement influence directement la satisfaction et la confiance client.',
      },
      fraud: {
        oneLiner: 'Cet indicateur suit les signaux de risque ou de fraude detectes dans les conversations.',
        importance: 'Il aide a proteger les clients et a anticiper les situations qui necessitent une vigilance renforcee.',
        recommendationHigh: 'Le niveau reste sous controle. Continuez la surveillance proactive des signaux sensibles.',
        recommendationLow: 'Renforcez les alertes precoces et les messages de prevention sur les parcours a risque.',
        aiAnalysis: '🤖 Analyse AELON: la surveillance fraude contribue directement a la securite client et a la reduction du risque operationnel.',
      },
      generic: {
        oneLiner: 'Cet indicateur vous aide a lire simplement la qualite du service rendu par AELON.',
        importance: 'Il permet de prendre des decisions metier plus rapides et plus sereines.',
        recommendationHigh: 'Indicateur satisfaisant. Continuez les bonnes pratiques actuelles.',
        recommendationLow: 'Planifiez une action ciblee pour faire progresser ce resultat au prochain cycle.',
        aiAnalysis: '🤖 Analyse AELON: cet indicateur aide a prioriser les actions metier les plus utiles pour les utilisateurs.',
      },
    };
    return templates[key] || templates.generic;
  }

  function buildPayload(title, details, context) {
    const score = Number.isFinite(context.score) ? context.score : null;
    const status = computeStatus(score);
    const scoreText = Number.isFinite(score) ? `${Math.round(score)} %` : 'indisponible';
    const key = semanticKey(title);
    const template = humanTemplate(title);

    const oneLiner = safeText(
      details.oneLiner,
      template.oneLiner
    );

    const resultText = safeText(
      details.result,
      Number.isFinite(score)
        ? `Votre score actuel est de ${scoreText}. La situation est ${statusBusinessLabel(status)} sur cet indicateur.`
        : 'Le score n est pas encore disponible. AELON attend davantage de données pour fournir un diagnostic fiable.'
    );

    const importance = safeText(
      details.importance,
      template.importance
    );

    const impact = Array.isArray(details.impact) && details.impact.length
      ? details.impact
      : buildDefaultImpact(title);

    const enterpriseImpact = Array.isArray(details.enterpriseImpact) && details.enterpriseImpact.length
      ? details.enterpriseImpact
      : buildEnterpriseImpact(title);

    const example = details.example || bankingExampleByKey(key);

    const recommendation = safeText(
      details.recommendation || details.action,
      Number.isFinite(score) && score >= 85
        ? template.recommendationHigh
        : template.recommendationLow
    );

    const aiAnalysis = safeText(
      details.aiAnalysis,
      template.aiAnalysis
    );

    const learnMore = safeText(
      details.learnMore,
      'AELON recalcule cet indicateur automatiquement a partir des conversations et des reponses produites. L objectif est de suivre une tendance metier dans le temps, pas seulement une valeur ponctuelle.'
    );

    return {
      status,
      oneLiner,
      resultText,
      importance,
      impact,
      enterpriseImpact,
      example,
      recommendation,
      aiAnalysis,
      learnMore,
    };
  }

  function ensureModal() {
    let modal = document.getElementById(modalId);
    if (modal) return modal;

    modal = document.createElement('div');
    modal.id = modalId;
    modal.className = 'aelon-kpi-modal';
    modal.innerHTML = `
      <div class="aelon-kpi-modal-card" role="dialog" aria-modal="true" aria-labelledby="aelonKpiModalTitle">
        <button type="button" class="aelon-kpi-modal-close" data-close>✓ J'ai compris</button>
        <h3 id="aelonKpiModalTitle">Indicateur</h3>
        <div class="aelon-kpi-modal-status" id="aelonKpiModalStatus"></div>
        <div class="aelon-kpi-modal-body"></div>
        <div class="aelon-kpi-modal-actions">
          <button type="button" class="aelon-kpi-learn-more" id="aelonKpiLearnMoreBtn">📖 En savoir plus</button>
        </div>
        <div class="aelon-kpi-learn-more-panel" id="aelonKpiLearnMorePanel" hidden></div>
      </div>
    `;

    modal.addEventListener('click', (event) => {
      if (event.target === modal || event.target.closest('[data-close]')) {
        modal.classList.remove('open');
      }
    });

    document.body.appendChild(modal);
    return modal;
  }

  function openKpiModal(title, details, context) {
    const modal = ensureModal();
    const titleEl = modal.querySelector('#aelonKpiModalTitle');
    const statusEl = modal.querySelector('#aelonKpiModalStatus');
    const bodyEl = modal.querySelector('.aelon-kpi-modal-body');
    const learnMoreBtn = modal.querySelector('#aelonKpiLearnMoreBtn');
    const learnMorePanel = modal.querySelector('#aelonKpiLearnMorePanel');
    if (!titleEl || !statusEl || !bodyEl || !learnMoreBtn || !learnMorePanel) return;

    const payload = buildPayload(title, details || {}, context || {});

    titleEl.textContent = toBusinessTitle(title);
    statusEl.className = `aelon-kpi-modal-status ${payload.status.className}`;
    statusEl.textContent = `${payload.status.icon} ${payload.status.label}`;

    bodyEl.innerHTML = `
      <section>
        <h4>1. En une phrase</h4>
        <p>${payload.oneLiner}</p>
      </section>
      <section>
        <h4>2. Ce que cela signifie</h4>
        <p>${payload.resultText}</p>
      </section>
      <section>
        <h4>3. Pourquoi c'est important</h4>
        <p>${payload.importance}</p>
      </section>
      <section>
        <h4>4. Impact utilisateur</h4>
        <ul>
          ${payload.impact.map((item) => `<li>✅ ${item}</li>`).join('')}
        </ul>
      </section>
      <section>
        <h4>5. Impact entreprise</h4>
        <ul>
          ${payload.enterpriseImpact.map((item) => `<li>🏢 ${item}</li>`).join('')}
        </ul>
      </section>
      <section>
        <h4>6. Exemple concret</h4>
        <p><strong>Question:</strong> ${safeText(payload.example.question, '-')}</p>
        <p><strong>Documents attendus:</strong> ${safeText(payload.example.expected, '-')}</p>
        <p><strong>Documents utilises:</strong> ${safeText(payload.example.used, '-')}</p>
        <p><strong>Resultat:</strong> ${safeText(payload.example.result, '-')}</p>
      </section>
      <section>
        <h4>7. Recommandation AELON</h4>
        <p>${payload.recommendation}</p>
      </section>
      <section>
        <h4>8. Analyse AELON</h4>
        <p>${payload.aiAnalysis}</p>
      </section>
    `;

    learnMorePanel.textContent = payload.learnMore;
    learnMorePanel.hidden = true;
    learnMoreBtn.textContent = '📖 En savoir plus';
    learnMoreBtn.onclick = () => {
      const isHidden = learnMorePanel.hidden;
      learnMorePanel.hidden = !isHidden;
      learnMoreBtn.textContent = isHidden ? '📖 Masquer le detail' : '📖 En savoir plus';
    };

    modal.classList.add('open');
  }

  function renderSynthesis(targetEl, payload) {
    if (!targetEl) return;
    const positives = Array.isArray(payload.positives) ? payload.positives : [];
    const warnings = Array.isArray(payload.warnings) ? payload.warnings : [];
    targetEl.innerHTML = `
      <h3>🧠 Synthese AELON</h3>
      <ul class="aelon-synthesis-list">
        ${positives.map((item) => `<li>✅ ${item}</li>`).join('')}
        ${warnings.map((item) => `<li>⚠️ ${item}</li>`).join('')}
      </ul>
      <p class="aelon-priority-action"><strong>🎯 Action prioritaire :</strong> ${payload.priorityAction || '-'}</p>
    `;
  }

  function bindViewMode(onChange) {
    const radios = document.querySelectorAll('input[name="aelon-view-mode"]');
    if (!radios.length) return 'business';

    const emit = () => {
      const checked = document.querySelector('input[name="aelon-view-mode"]:checked');
      const mode = checked ? checked.value : 'business';
      if (typeof onChange === 'function') onChange(mode);
    };

    radios.forEach((radio) => {
      radio.addEventListener('change', emit);
    });

    emit();
    return 'business';
  }

  function renderGuide(targetEl) {
    if (!targetEl) return;
    targetEl.innerHTML = `
      <h3>🎓 Comprendre AELON</h3>
      <ul class="aelon-guide-list">
        <li><strong>Comment fonctionne AELON ?</strong> AELON combine recherche documentaire et IA generative pour produire une reponse guidee par des sources.</li>
        <li><strong>Qu'est-ce que l'IA generative ?</strong> C'est une IA qui formule des reponses naturelles a partir d'instructions et de contexte.</li>
        <li><strong>Comment AELON trouve ses informations ?</strong> AELON consulte d abord les contenus utiles, puis construit une reponse claire a partir de ces references.</li>
        <li><strong>Comment sont calcules les scores ?</strong> Chaque score mesure un aspect metier: fiabilite des informations, comprehension des demandes, qualite des reponses et rapidite de traitement.</li>
        <li><strong>Que signifient les KPI ?</strong> Chaque KPI a une fiche explicative accessible via le bouton ⓘ.</li>
      </ul>
    `;
  }

  function setupKpiInteractions(container, getMeta) {
    if (!container) return;
    container.querySelectorAll('[data-kpi-id]').forEach((card) => {
      const id = card.getAttribute('data-kpi-id');
      const open = () => {
        const meta = typeof getMeta === 'function' ? getMeta(id, card) : null;
        if (!meta) return;
        const rawScore = card.getAttribute('data-kpi-score');
        openKpiModal(meta.title, meta.details || {}, { score: toNumber(rawScore) });
      };

      card.addEventListener('click', (event) => {
        if (event.target.closest('button') || event.target.closest('.aelon-kpi-help')) {
          open();
          return;
        }
        open();
      });

      const help = card.querySelector('.aelon-kpi-help');
      if (help) {
        help.setAttribute('title', help.getAttribute('data-tooltip') || 'Cliquez pour comprendre cet indicateur');
      }
    });
  }

  window.AelonExplainability = {
    bindViewMode,
    renderSynthesis,
    renderGuide,
    setupKpiInteractions,
    openKpiModal,
  };
})();
