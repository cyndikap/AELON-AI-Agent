document.addEventListener('DOMContentLoaded', async () => {
  const tabs = document.querySelectorAll('.governance-tab');
  const panels = document.querySelectorAll('.governance-panel');
  const history = document.getElementById('governanceChatHistory');
  const retrievalRateValue = document.getElementById('retrievalRateValue');
  const documentsUsedValue = document.getElementById('documentsUsedValue');
  const avgContextValue = document.getElementById('avgContextValue');
  const withSourcesValue = document.getElementById('withSourcesValue');
  const withoutSourcesValue = document.getElementById('withoutSourcesValue');
  const emptyRetrievalValue = document.getElementById('emptyRetrievalValue');
  const sourcesCitedValue = document.getElementById('sourcesCitedValue');

  tabs.forEach((tab) => {
    tab.addEventListener('click', () => {
      const target = tab.dataset.tab;
      tabs.forEach((button) => button.classList.toggle('active', button === tab));
      panels.forEach((panel) => panel.classList.toggle('active', panel.id === `gov-${target}`));
    });
  });

  const addBubble = (text) => {
    const bubble = document.createElement('div');
    bubble.className = 'governance-chat-message';
    bubble.textContent = text;
    history.appendChild(bubble);
  };

  try {
    const response = await fetch('/governance');
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();
    if (retrievalRateValue) retrievalRateValue.textContent = `${Number(data.retrieval_success_rate || 0).toFixed(2)}%`;
    if (documentsUsedValue) documentsUsedValue.textContent = Number(data.avg_documents_retrieved || 0).toFixed(2);
    if (avgContextValue) avgContextValue.textContent = `${Number(data.avg_context_chars || 0).toFixed(0)} chars`;
    if (withSourcesValue) withSourcesValue.textContent = String(data.responses_with_sources || 0);
    if (withoutSourcesValue) withoutSourcesValue.textContent = String(data.responses_without_sources || 0);
    if (emptyRetrievalValue) emptyRetrievalValue.textContent = `${Number(data.retrieval_empty_rate || 0).toFixed(2)}%`;

    const citations = Array.isArray(data.citations_per_source) ? data.citations_per_source : [];
    if (sourcesCitedValue) {
      sourcesCitedValue.textContent = citations.length > 0
        ? citations.map((item) => `${item.source} (${item.count})`).slice(0, 2).join(', ')
        : 'Aucune';
    }

    addBubble(`Retrieval rate: ${Number(data.retrieval_success_rate || 0).toFixed(2)}%`);
    addBubble(`Documents moyens récupérés: ${Number(data.avg_documents_retrieved || 0).toFixed(2)}`);
    addBubble(`Contexte moyen (chars): ${Number(data.avg_context_chars || 0).toFixed(0)}`);

    const topCitations = Array.isArray(data.citations_per_source) ? data.citations_per_source.slice(0, 3) : [];
    if (topCitations.length > 0) {
      topCitations.forEach((item) => {
        addBubble(`Source citée: ${item.source} (${item.count})`);
      });
    } else {
      addBubble('Aucune citation source disponible pour le moment.');
    }
  } catch (error) {
    addBubble('Impossible de charger les KPI Governance pour le moment.');
    if (retrievalRateValue) retrievalRateValue.textContent = 'Indisponible';
    if (documentsUsedValue) documentsUsedValue.textContent = 'Indisponible';
    if (avgContextValue) avgContextValue.textContent = 'Indisponible';
    if (withSourcesValue) withSourcesValue.textContent = 'Indisponible';
    if (withoutSourcesValue) withoutSourcesValue.textContent = 'Indisponible';
    if (emptyRetrievalValue) emptyRetrievalValue.textContent = 'Indisponible';
    if (sourcesCitedValue) sourcesCitedValue.textContent = 'Indisponible';
  }
});
