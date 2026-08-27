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
      label: 'Evaluation Copilot',
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
      <div class="copilot-assistant-section-title">💡 Questions suggerees</div>
      <div class="copilot-assistant-questions"></div>
      <div class="copilot-assistant-section-title">💬 Historique de conversation</div>
      <div class="copilot-assistant-history" role="log" aria-live="polite"></div>
      <form class="copilot-assistant-input" autocomplete="off">
        <input type="text" class="copilot-assistant-textbox" placeholder="Posez votre question..." aria-label="Posez votre question" />
        <button type="submit" class="copilot-assistant-send">Envoyer</button>
      </form>
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

    const historyEl = panel.querySelector('.copilot-assistant-history');
    const closeEl = panel.querySelector('.copilot-assistant-close');
    const questionsEl = panel.querySelector('.copilot-assistant-questions');
    const inputFormEl = panel.querySelector('.copilot-assistant-input');
    const inputEl = panel.querySelector('.copilot-assistant-textbox');
    const sendEl = panel.querySelector('.copilot-assistant-send');

    let isAsking = false;
    const turns = [];

    const setBusyState = (busy) => {
      isAsking = busy;
      if (inputEl) inputEl.disabled = busy;
      if (sendEl) sendEl.disabled = busy;
      if (!questionsEl) return;
      questionsEl.querySelectorAll('button').forEach((button) => {
        button.disabled = busy;
      });
    };

    const addTurn = (role, text, opts = {}) => {
      if (!historyEl) return null;
      const row = document.createElement('div');
      row.className = `copilot-assistant-msg ${role}${opts.typing ? ' typing' : ''}`;
      const bubble = document.createElement('div');
      bubble.className = 'copilot-assistant-bubble';
      bubble.textContent = opts.typing ? 'Analyse en cours...' : String(text || '').trim();
      row.appendChild(bubble);
      historyEl.appendChild(row);
      historyEl.scrollTop = historyEl.scrollHeight;
      return row;
    };

    const buildHistoryPayload = () => turns.map((turn) => ({ role: turn.role, content: turn.content }));

    const askQuestion = async (question) => {
      const userText = String(question || '').trim();
      if (!userText || isAsking || !historyEl) return;

      addTurn('user', userText);
      turns.push({ role: 'user', content: userText });

      if (inputEl) {
        inputEl.value = '';
      }

      setBusyState(true);
      const typingRow = addTurn('assistant', '', { typing: true });

      try {
        let responseText = 'Aucune recommandation disponible.';
        if (typeof onAsk === 'function') {
          const response = await onAsk(userText, {
            mode,
            history: buildHistoryPayload(),
          });
          const normalized = String(response || '').trim();
          responseText = normalized || responseText;
        }
        if (typingRow) typingRow.remove();
        addTurn('assistant', responseText);
        turns.push({ role: 'assistant', content: responseText });
      } catch (_error) {
        if (typingRow) typingRow.remove();
        const errorText = 'Une erreur est survenue pendant l analyse.';
        addTurn('assistant', errorText);
        turns.push({ role: 'assistant', content: errorText });
      } finally {
        setBusyState(false);
        if (inputEl) inputEl.focus();
      }
    };

    if (historyEl) {
      const intro = initialMessage || 'Selectionnez une question pour demarrer la conversation.';
      addTurn('assistant', intro);
      turns.push({ role: 'assistant', content: intro });
    }

    if (questionsEl) {
      questions.forEach((question) => {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'copilot-assistant-question';
        button.textContent = question;
        button.addEventListener('click', () => {
          askQuestion(question);
        });
        questionsEl.appendChild(button);
      });
    }

    if (inputFormEl && inputEl) {
      inputFormEl.addEventListener('submit', (event) => {
        event.preventDefault();
        askQuestion(inputEl.value);
      });
    }

    const open = () => {
      panel.classList.add('open');
      overlay.classList.add('open');
      panel.setAttribute('aria-hidden', 'false');
      overlay.setAttribute('aria-hidden', 'false');
      if (inputEl) inputEl.focus();
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
