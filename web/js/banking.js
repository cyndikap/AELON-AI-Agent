document.addEventListener('DOMContentLoaded', () => {
  const chatInput = document.getElementById('bankingChatInput');
  const chatForm = document.getElementById('bankingChatForm');
  const messages = document.getElementById('bankingMessages');
  const quickActions = document.querySelectorAll('.banking-quick-action');
  const quickActionsContainer = document.querySelector('.banking-quick-actions');
  let hasUserInteracted = false;
  const sessionStorageKey = 'aelon_session_id';
  let sessionId = localStorage.getItem(sessionStorageKey);
  if (!sessionId) {
    sessionId = `sess-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
    localStorage.setItem(sessionStorageKey, sessionId);
  }

  const hideQuickActions = () => {
    if (!quickActionsContainer) return;
    quickActionsContainer.classList.add('is-hidden');
  };

  const addMessage = (sender, text) => {
    const row = document.createElement('div');
    row.className = `banking-message-row ${sender}`;

    if (sender === 'assistant') {
      const avatar = document.createElement('div');
      avatar.className = 'banking-avatar';
      avatar.innerHTML = '<img src="/static/aelon-icon.svg" alt="AELON" />';
      row.appendChild(avatar);
    }

    const bubble = document.createElement('div');
    bubble.className = `banking-message ${sender}`;
    bubble.textContent = text;
    row.appendChild(bubble);
    messages.appendChild(row);
    messages.scrollTop = messages.scrollHeight;
  };

  const sendToBackend = async (value) => {
    try {
      const response = await fetch('/web/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-session-id': sessionId,
        },
        body: JSON.stringify({ query: value }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      const answer = data.answer || 'Je n’ai pas pu générer de réponse pour le moment.';
      addMessage('assistant', answer);
      return answer;
    } catch (error) {
      addMessage('assistant', 'Une erreur est survenue lors du traitement de votre demande. Merci de réessayer dans un instant.');
      return null;
    }
  };

  const welcomeMessage = 'Bonjour et bienvenue sur AELON.\n\nJe suis votre assistant bancaire intelligent, conçu pour répondre rapidement à vos demandes, sécuriser votre expérience et vous orienter avec précision.';
  if (!messages.innerHTML.trim()) {
    addMessage('assistant', welcomeMessage);
  }

  quickActions.forEach((button) => {
    button.addEventListener('click', async () => {
      const value = button.dataset.question || button.textContent.trim();
      if (!value) return;

      if (!hasUserInteracted) {
        hasUserInteracted = true;
        hideQuickActions();
      }

      addMessage('user', value);
      await sendToBackend(value);
    });
  });

  chatForm.addEventListener('submit', async (event) => {
    event.preventDefault();
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
