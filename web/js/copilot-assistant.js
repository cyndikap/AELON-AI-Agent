(function registerCopilotAssistant(global) {
  const MODE_CONFIG = {
    analytics: {
      icon: '🤖',
      label: 'AI Insights',
      title: 'AI Insights',
      kicker: 'Analytics Copilot',
      color: 'linear-gradient(135deg, #6236ff 0%, #8c5cff 58%, #b790ff 100%)',
    },
    governance: {
      icon: '🛡️',
      label: 'Governance Assistant',
      title: 'Governance Assistant',
      kicker: 'Governance Assistant',
      color: 'linear-gradient(135deg, #7a1128 0%, #a91f42 52%, #cc4764 100%)',
    },
    evaluation: {
      icon: '📈',
      label: 'Evaluation Chat',
      title: 'Evaluation Copilot',
      kicker: 'Evaluation Copilot',
      color: 'linear-gradient(135deg, #007f79 0%, #00a99e 52%, #3fc9bd 100%)',
    },
  };

  function create({ mode = 'analytics', questions = [], onAsk, initialMessage = '' }) {
    const theme = MODE_CONFIG[mode] || MODE_CONFIG.analytics;

    const overlay = document.createElement('div');
    overlay.className = 'copilot-assistant-overlay';
    overlay.setAttribute('aria-hidden', 'true');

    const panel = document.createElement('aside');
    panel.className = 'copilot-assistant-panel';
    panel.setAttribute('aria-hidden', 'true');
    panel.innerHTML = `
      <div class="copilot-assistant-head">
        <div>
          <div class="copilot-assistant-kicker">${theme.kicker}</div>
          <h3>${theme.title}</h3>
        </div>
        <button class="copilot-assistant-close" type="button" aria-label="Fermer">×</button>
      </div>
      <div class="copilot-assistant-questions"></div>
      <div class="copilot-assistant-answer"></div>
    `;

    const fab = document.createElement('button');
    fab.type = 'button';
    fab.className = 'copilot-assistant-fab';
    fab.setAttribute('aria-label', `Ouvrir ${theme.label}`);
    fab.style.background = theme.color;
    fab.innerHTML = `
      <span class="copilot-assistant-fab-icon">${theme.icon}</span>
      <span class="copilot-assistant-fab-label">${theme.label}</span>
    `;

    document.body.appendChild(overlay);
    document.body.appendChild(panel);
    document.body.appendChild(fab);

    const answerEl = panel.querySelector('.copilot-assistant-answer');
    const closeEl = panel.querySelector('.copilot-assistant-close');
    const questionsEl = panel.querySelector('.copilot-assistant-questions');

    answerEl.textContent = initialMessage || 'Selectionnez une question pour afficher une analyse immediate.';

    questions.forEach((question) => {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'copilot-assistant-question';
      button.textContent = question;
      button.addEventListener('click', async () => {
        answerEl.textContent = 'Analyse en cours...';
        try {
          if (typeof onAsk === 'function') {
            const response = await onAsk(question);
            answerEl.textContent = (response || '').toString().trim() || 'Aucune recommandation disponible.';
          } else {
            answerEl.textContent = 'Aucune recommandation disponible.';
          }
        } catch (_error) {
          answerEl.textContent = 'Une erreur est survenue pendant l analyse.';
        }
      });
      questionsEl.appendChild(button);
    });

    const open = () => {
      panel.classList.add('open');
      overlay.classList.add('open');
      panel.setAttribute('aria-hidden', 'false');
      overlay.setAttribute('aria-hidden', 'false');
    };

    const close = () => {
      panel.classList.remove('open');
      overlay.classList.remove('open');
      panel.setAttribute('aria-hidden', 'true');
      overlay.setAttribute('aria-hidden', 'true');
    };

    fab.addEventListener('click', open);
    closeEl.addEventListener('click', close);
    overlay.addEventListener('click', close);

    return {
      open,
      close,
      destroy() {
        fab.remove();
        panel.remove();
        overlay.remove();
      },
    };
  }

  global.CopilotAssistant = { create };
})(window);
