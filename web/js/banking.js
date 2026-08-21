document.addEventListener('DOMContentLoaded', () => {
  const chatInput = document.getElementById('bankingChatInput');
  const chatForm = document.getElementById('bankingChatForm');
  const messages = document.getElementById('bankingMessages');
  const quickActions = document.querySelectorAll('.banking-quick-action');
  const quickActionsContainer = document.querySelector('.banking-quick-actions');
  const streamingEnabled = true;
  let isSending = false;
  let hasUserInteracted = false;
  const sessionStorageKey = 'aelon_session_id';
  let sessionId = localStorage.getItem(sessionStorageKey);
  if (!sessionId) {
    sessionId = `sess-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
    localStorage.setItem(sessionStorageKey, sessionId);
  }

  const placeholderMap = {
    '[ACCOUNT_NUMBER]': 'votre etablissement bancaire',
    '[BANK_ACCOUNT]': 'votre etablissement bancaire',
    '[CARD_NUMBER]': 'votre etablissement bancaire',
    '[PHONE_NUMBER]': 'le service client de votre banque',
    '[PHONE]': 'le service client de votre banque',
    '[EMAIL]': 'votre adresse e-mail',
    '[PERSON]': 'votre conseiller bancaire',
  };

  const hideQuickActions = () => {
    if (!quickActionsContainer) return;
    quickActionsContainer.classList.add('is-hidden');
  };

  const normalizeText = (value) => {
    let out = (value || '').toString();
    Object.entries(placeholderMap).forEach(([token, replacement]) => {
      out = out.split(token).join(replacement);
    });
    out = out.replace(/\[[A-Z0-9_]+\]/g, 'les informations necessaires');
    out = out.replace(/\s+([,;:.!?])/g, '$1').replace(/\s{2,}/g, ' ').trim();
    return out;
  };

  const normalizeSources = (rawSources) => {
    if (!Array.isArray(rawSources)) return [];
    const unique = new Set();
    return rawSources
      .map((item) => {
        if (!item || typeof item !== 'object') return null;
        const source = (item.source || '').toString().trim();
        const category = (item.category || item.categorie || '').toString().trim();
        if (!source) return null;
        const key = `${source}::${category}`;
        if (unique.has(key)) return null;
        unique.add(key);
        return { source, category };
      })
      .filter(Boolean)
      .slice(0, 4);
  };

  const scrollToBottom = () => {
    messages.scrollTop = messages.scrollHeight;
  };

  const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
  const requestTimeoutMs = 65000;

  const appendSourcesToBubble = (bubble, sources) => {
    const cleanSources = normalizeSources(sources);
    if (!cleanSources.length) return;

    const sourcesBlock = document.createElement('div');
    sourcesBlock.className = 'banking-sources';

    const sourceTitle = document.createElement('div');
    sourceTitle.className = 'banking-sources-title';
    sourceTitle.textContent = 'Sources';
    sourcesBlock.appendChild(sourceTitle);

    const sourceList = document.createElement('div');
    sourceList.className = 'banking-sources-list';
    cleanSources.forEach((entry) => {
      const chip = document.createElement('span');
      chip.className = 'banking-source-chip';
      chip.textContent = entry.category ? `${entry.category}: ${entry.source}` : entry.source;
      sourceList.appendChild(chip);
    });

    sourcesBlock.appendChild(sourceList);
    bubble.appendChild(sourcesBlock);
  };

  const addMessage = (sender, text, options = {}) => {
    const { typing = false, sources = [] } = options;

    const row = document.createElement('div');
    row.className = `banking-message-row ${sender}`;
    if (typing) row.classList.add('typing-row');

    const avatar = document.createElement('div');
    avatar.className = sender === 'assistant' ? 'banking-avatar assistant' : 'banking-avatar user';
    avatar.innerHTML = sender === 'assistant'
      ? '<img src="/static/aelon-icon.svg" alt="AELON" />'
      : '<span aria-hidden="true">VOUS</span>';

    if (sender === 'assistant') {
      row.appendChild(avatar);
    }

    const bubble = document.createElement('div');
    bubble.className = `banking-message ${sender}`;

    if (typing) {
      bubble.innerHTML = '<span class="typing-copy">AELON analyse votre demande</span><span class="typing-dots" aria-hidden="true"><i></i><i></i><i></i></span>';
    } else {
      const messageContent = document.createElement('div');
      messageContent.textContent = normalizeText(text);
      bubble.appendChild(messageContent);

      if (sender === 'assistant') {
        appendSourcesToBubble(bubble, sources);
      }
    }

    row.appendChild(bubble);

    if (sender === 'user') {
      row.appendChild(avatar);
    }

    messages.appendChild(row);
    scrollToBottom();
    return row;
  };

  const streamAssistantMessage = async (text, sources = []) => {
    const row = addMessage('assistant', '');
    const bubble = row.querySelector('.banking-message.assistant');
    const content = bubble?.querySelector('div');
    if (!bubble || !content) return;

    const normalized = normalizeText(text || 'Je n ai pas pu generer de reponse pour le moment.');
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const tokens = normalized.match(/\S+\s*/g) || [normalized];

    if (!streamingEnabled || reducedMotion || tokens.length < 3) {
      content.textContent = normalized;
      appendSourcesToBubble(bubble, sources);
      scrollToBottom();
      return;
    }

    bubble.classList.add('streaming');
    content.textContent = '';

    for (let i = 0; i < tokens.length; i += 1) {
      content.textContent += tokens[i];
      scrollToBottom();

      if (i === tokens.length - 1) {
        break;
      }

      const token = tokens[i];
      let delay = 16;
      if (/[.!?]\s*$/.test(token)) {
        delay = 78;
      } else if (/[,;:]\s*$/.test(token)) {
        delay = 42;
      } else if (i > 120) {
        delay = 8;
      }
      await wait(delay);
    }

    bubble.classList.remove('streaming');
    appendSourcesToBubble(bubble, sources);
    scrollToBottom();
  };

  const sendToBackend = async (value) => {
    isSending = true;
    const typingRow = addMessage('assistant', '', { typing: true });
    if (chatInput) chatInput.disabled = true;

    const callChatApi = async () => {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), requestTimeoutMs);
      try {
        const response = await fetch('/web/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'x-session-id': sessionId,
          },
          body: JSON.stringify({ query: value }),
          signal: controller.signal,
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        return await response.json();
      } finally {
        clearTimeout(timeoutId);
      }
    };

    try {
      let data;
      try {
        data = await callChatApi();
      } catch (error) {
        // One silent retry for long-running model inference that exceeded timeout.
        if (error?.name !== 'AbortError') {
          throw error;
        }
        data = await callChatApi();
      }
      typingRow.remove();
      await streamAssistantMessage(data.answer || 'Je n ai pas pu generer de reponse pour le moment.', data.sources || []);
      return data;
    } catch (_error) {
      typingRow.remove();
      await streamAssistantMessage('Le delai de reponse est depasse ou une erreur est survenue. Merci de reessayer dans un instant.');
      return null;
    } finally {
      isSending = false;
      if (chatInput) {
        chatInput.disabled = false;
        chatInput.focus();
      }
    }
  };

  const welcomeMessage = 'Bonjour et bienvenue sur AELON.\n\nJe suis votre assistant bancaire intelligent. Je vous accompagne pour les cartes bancaires, les virements, les acces au compte et les demandes de support du quotidien.';
  if (!messages.innerHTML.trim()) {
    addMessage('assistant', welcomeMessage);
  }

  quickActions.forEach((button) => {
    button.addEventListener('click', async () => {
      if (isSending) return;
      const value = (button.dataset.question || button.textContent || '').trim();
      if (!value) return;

      if (!hasUserInteracted) {
        hasUserInteracted = true;
        hideQuickActions();
      }

      addMessage('user', value);
      button.disabled = true;
      await sendToBackend(value);
    });
  });

  chatForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    if (isSending) return;
    const value = chatInput.value.trim();
    if (!value) return;

    if (!hasUserInteracted) {
      hasUserInteracted = true;
      hideQuickActions();
    }

    addMessage('user', value);
    chatInput.value = '';
    await sendToBackend(value);
  });
});
