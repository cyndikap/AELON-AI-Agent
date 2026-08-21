const messagesEl = document.getElementById('messages');
const chatForm = document.getElementById('chatForm');
const chatInput = document.getElementById('chatInput');
const quickButtons = document.querySelectorAll('.btn-quick');
const premiumQuickButtons = document.querySelectorAll('.quick-action');
const spaceButtons = document.querySelectorAll('.nav-space');
const spaceScreens = document.querySelectorAll('.space-screen');
const activeRoleLabel = document.getElementById('activeRoleLabel');
const customerQuickBlock = document.getElementById('customerQuickBlock');
const themeToggleBtn = document.getElementById('themeToggle');

const analyticsKpis = document.getElementById('analyticsKpis');
const analyticsCategories = document.getElementById('analyticsCategories');
const analyticsSentiments = document.getElementById('analyticsSentiments');
const analyticsTrends = document.getElementById('analyticsTrends');
const analyticsChatHistory = document.getElementById('analyticsCopilotHistory');
const analyticsChatForm = document.getElementById('analyticsCopilotForm');
const analyticsChatInput = document.getElementById('analyticsCopilotInput');
const analyticsPromptChips = document.querySelectorAll('#analyticsPromptChips .prompt-chip');

const governanceChatHistory = document.getElementById('governanceCopilotHistory');
const governanceChatForm = document.getElementById('governanceCopilotForm');
const governanceChatInput = document.getElementById('governanceCopilotInput');
const govTabButtons = document.querySelectorAll('.gov-tab');
const govEvaluation = document.getElementById('gov-evaluation');
const govObservability = document.getElementById('gov-observability');
const govDataQuality = document.getElementById('gov-dataquality');

const filterStartDate = document.getElementById('filterStartDate');
const filterEndDate = document.getElementById('filterEndDate');
const filterCategory = document.getElementById('filterCategory');
const filterSentiment = document.getElementById('filterSentiment');
const filterAgent = document.getElementById('filterAgent');
const applyFiltersBtn = document.getElementById('applyFilters');
const resetFiltersBtn = document.getElementById('resetFilters');

const exportAnalyticsCsvBtn = document.getElementById('exportAnalyticsCsv');
const exportAnalyticsPdfBtn = document.getElementById('exportAnalyticsPdf');
const exportGovernanceCsvBtn = document.getElementById('exportGovernanceCsv');
const exportGovernancePdfBtn = document.getElementById('exportGovernancePdf');

let analyticsRows = [];
let filteredAnalyticsRows = [];
let governanceData = null;
let activeSpace = 'customer';
let realtimeTimer = null;
let spaceTransitionTimer = null;

const analyticsChartIds = [
  'chartVolumeTimeline',
  'chartActivityHeatmap',
  'chartCategoriesPie',
  'chartSentimentsDonut',
  'chartFraudHistogram',
];
const staggerGroups = document.querySelectorAll('.stagger-group');

const privacyDisplayMap = {
  '[PHONE_NUMBER]': 'le service client de votre banque',
  '[PHONE]': 'le service client de votre banque',
  '[PERSON]': 'votre conseiller bancaire',
  '[BANK_ACCOUNT]': 'votre etablissement bancaire',
  '[ACCOUNT_NUMBER]': 'votre etablissement bancaire',
  '[EMAIL]': 'votre adresse e-mail',
  '[CARD_NUMBER]': 'votre etablissement bancaire',
};

function safeText(v) {
  return (v || '').toString();
}

function safeNum(v, d = 0) {
  const n = Number(v);
  return Number.isFinite(n) ? n : d;
}

function normalizeMaskedText(value) {
  let out = safeText(value);
  Object.entries(privacyDisplayMap).forEach(([source, target]) => {
    out = out.split(source).join(target);
  });
  out = out.replace(/\[[A-Z0-9_]+\]/g, 'les informations necessaires');
  out = out.replace(/\s+([,;:.!?])/g, '$1').replace(/\s{2,}/g, ' ').trim();
  return out;
}

function normalizeSources(rawSources) {
  if (!Array.isArray(rawSources)) return [];
  const seen = new Set();
  return rawSources
    .map((item) => {
      if (!item || typeof item !== 'object') return null;
      const source = safeText(item.source).trim();
      const category = safeText(item.category || item.categorie || '').trim();
      if (!source) return null;
      const key = `${source}::${category}`;
      if (seen.has(key)) return null;
      seen.add(key);
      return { source, category };
    })
    .filter(Boolean)
    .slice(0, 4);
}

function addCustomerMessage(role, text, options = {}) {
  const { typing = false, sources = [] } = options;
  const row = document.createElement('div');
  row.className = `message-row ${role}`;
  if (typing) {
    row.classList.add('typing-row');
  }

  const avatar = document.createElement('div');
  avatar.className = role === 'assistant' ? 'assistant-avatar' : 'user-avatar';
  avatar.innerHTML = role === 'assistant'
    ? '<img src="/static/aelon-icon.svg" alt="AELON logo" />'
    : '<span aria-hidden="true">VOUS</span>';

  if (role === 'assistant') row.appendChild(avatar);

  const wrapper = document.createElement('div');
  wrapper.className = `message ${role}`;
  if (typing) wrapper.classList.add('typing-bubble');

  const content = document.createElement('div');
  if (typing) {
    content.innerHTML = '<span class="typing-copy">AELON analyse votre demande</span><span class="typing-dots" aria-hidden="true"><i></i><i></i><i></i></span>';
  } else {
    content.textContent = normalizeMaskedText(text);
  }
  wrapper.appendChild(content);

  if (role === 'assistant' && !typing) {
    const cleanSources = normalizeSources(sources);
    if (cleanSources.length) {
      const citationBox = document.createElement('div');
      citationBox.className = 'message-sources';
      const citationTitle = document.createElement('div');
      citationTitle.className = 'message-sources-title';
      citationTitle.textContent = 'Sources';
      citationBox.appendChild(citationTitle);

      const citationList = document.createElement('div');
      citationList.className = 'message-sources-list';
      cleanSources.forEach((entry) => {
        const chip = document.createElement('span');
        chip.className = 'message-source-chip';
        chip.textContent = entry.category ? `${entry.category}: ${entry.source}` : entry.source;
        citationList.appendChild(chip);
      });
      citationBox.appendChild(citationList);
      wrapper.appendChild(citationBox);
    }
  }

  row.appendChild(wrapper);
  if (role === 'user') row.appendChild(avatar);

  messagesEl.appendChild(row);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  return row;
}

async function sendCustomerMessage(rawText) {
  const text = safeText(rawText).trim();
  if (!text) return;

  addCustomerMessage('user', text);
  chatInput.value = '';
  const typingIndicator = addCustomerMessage('assistant', '', { typing: true });

  try {
    const res = await fetch('/web/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: text }),
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    typingIndicator.remove();
    addCustomerMessage('assistant', safeText(data.answer), { sources: data.sources || [] });
  } catch (_err) {
    typingIndicator.remove();
    addCustomerMessage('assistant', 'Desole, une erreur est survenue. Merci de reessayer.');
  }
}

function renderRows(container, rows) {
  container.innerHTML = '';
  (rows || []).forEach((item) => {
    const row = document.createElement('div');
    row.className = 'list-row';
    const left = document.createElement('span');
    left.textContent = safeText(item.label || item.day || 'N/A');
    const right = document.createElement('strong');
    right.textContent = safeText(item.count ?? item.value ?? 0);
    row.appendChild(left);
    row.appendChild(right);
    container.appendChild(row);
  });
}

function renderAnalyticsSkeleton() {
  analyticsKpis.innerHTML = `
    <div class="skeleton-kpi"></div>
    <div class="skeleton-kpi"></div>
    <div class="skeleton-kpi"></div>
    <div class="skeleton-kpi"></div>
    <div class="skeleton-kpi"></div>
  `;

  [analyticsCategories, analyticsSentiments, analyticsTrends].forEach((container) => {
    container.innerHTML = `
      <div class="skeleton-line"></div>
      <div class="skeleton-line"></div>
      <div class="skeleton-line"></div>
    `;
  });

  analyticsChartIds.forEach((id) => {
    const chart = document.getElementById(id);
    if (chart) {
      chart.innerHTML = '<div class="chart-skeleton"></div>';
    }
  });
}

function renderGovernanceSkeleton() {
  [govEvaluation, govObservability, govDataQuality].forEach((panel) => {
    panel.innerHTML = `
      <div class="mini-title">Chargement...</div>
      <div class="list-rows">
        <div class="skeleton-line"></div>
        <div class="skeleton-line"></div>
        <div class="skeleton-line"></div>
        <div class="skeleton-line"></div>
      </div>
    `;
  });
}

function runStagger(group) {
  if (!group) return;
  group.classList.remove('is-visible');
  void group.offsetHeight;
  group.classList.add('is-visible');
}

function runAnalyticsStagger() {
  staggerGroups.forEach((g) => runStagger(g));
}

function setTheme(privateMode) {
  document.body.classList.toggle('private-theme', !!privateMode);
  if (themeToggleBtn) {
    themeToggleBtn.setAttribute('aria-pressed', privateMode ? 'true' : 'false');
    themeToggleBtn.innerHTML = privateMode
      ? '<i class="bi bi-bank2 me-2"></i>Theme standard'
      : '<i class="bi bi-bank2 me-2"></i>Theme banque privee';
  }
}

function initTheme() {
  const saved = localStorage.getItem('aelon-theme');
  setTheme(saved === 'private');
}

function chatPush(container, role, text) {
  const item = document.createElement('div');
  item.className = `copilot-item ${role}`;
  item.textContent = safeText(text);
  container.appendChild(item);
  container.scrollTop = container.scrollHeight;
}

function toIsoDay(ts) {
  const s = safeText(ts);
  return s.length >= 10 ? s.slice(0, 10) : s;
}

function downloadBlob(filename, content, mime) {
  const blob = new Blob([content], { type: mime });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

function toCsv(rows) {
  if (!rows.length) return 'timestamp,query,answer\n';
  const cols = Object.keys(rows[0]);
  const esc = (v) => `"${safeText(v).replaceAll('"', '""')}"`;
  const lines = [cols.join(',')];
  rows.forEach((r) => {
    lines.push(cols.map((c) => esc(r[c])).join(','));
  });
  return lines.join('\n');
}

function exportPdf(title, rows) {
  const jsPDF = window.jspdf?.jsPDF;
  if (!jsPDF) return;

  const doc = new jsPDF();
  doc.setFontSize(14);
  doc.text(title, 14, 16);
  doc.setFontSize(9);
  doc.text(`Genere le ${new Date().toLocaleString()}`, 14, 22);

  if (!rows.length) {
    doc.text('Aucune donnee.', 14, 30);
  } else {
    const cols = Object.keys(rows[0]);
    const body = rows.slice(0, 100).map((r) => cols.map((c) => safeText(r[c])));
    doc.autoTable({
      startY: 28,
      head: [cols],
      body,
      styles: { fontSize: 7 },
      headStyles: { fillColor: [10, 61, 145] },
    });
  }

  doc.save(`${title.replaceAll(' ', '_').toLowerCase()}.pdf`);
}

function setupFilterOptions(rows) {
  const fill = (selectEl, values) => {
    const current = selectEl.value;
    selectEl.innerHTML = '<option value="all">Tous</option>';
    values.forEach((v) => {
      const option = document.createElement('option');
      option.value = v;
      option.textContent = v;
      selectEl.appendChild(option);
    });
    if ([...selectEl.options].some((o) => o.value === current)) {
      selectEl.value = current;
    }
  };

  const categories = [...new Set(rows.map((r) => safeText(r.category || 'autre')))].sort();
  const sentiments = [...new Set(rows.map((r) => safeText(r.sentiment || 'neutral')))].sort();
  const agents = [...new Set(rows.map((r) => safeText(r.agent || 'unknown')))].sort();

  fill(filterCategory, categories);
  fill(filterSentiment, sentiments);
  fill(filterAgent, agents);
}

function applyFilters() {
  const start = filterStartDate.value;
  const end = filterEndDate.value;
  const category = filterCategory.value;
  const sentiment = filterSentiment.value;
  const agent = filterAgent.value;

  filteredAnalyticsRows = analyticsRows.filter((r) => {
    const day = toIsoDay(r.timestamp);
    if (start && day < start) return false;
    if (end && day > end) return false;
    if (category !== 'all' && safeText(r.category) !== category) return false;
    if (sentiment !== 'all' && safeText(r.sentiment) !== sentiment) return false;
    if (agent !== 'all' && safeText(r.agent) !== agent) return false;
    return true;
  });

  renderAnalyticsFromRows();
}

function summarizeRows(rows) {
  const total = rows.length;
  const escalades = rows.filter((r) => !!r.escalated).length;
  const fraudes = rows.filter((r) => !!r.is_fraud).length;
  const q = rows.map((r) => safeNum(r.answer_quality, 0));
  const quality = q.length ? q.reduce((a, b) => a + b, 0) / q.length : 0;

  const compValues = rows
    .map((r) => {
      if (Number.isFinite(Number(r.compliance_score))) return Number(r.compliance_score);
      if (typeof r.compliance === 'boolean') return r.compliance ? 100 : 0;
      return null;
    })
    .filter((v) => v !== null);
  const compliance = compValues.length
    ? compValues.reduce((a, b) => a + b, 0) / compValues.length
    : 100;

  const categories = {};
  const sentiments = {};
  rows.forEach((r) => {
    const c = safeText(r.category || 'autre');
    const s = safeText(r.sentiment || 'neutral');
    categories[c] = (categories[c] || 0) + 1;
    sentiments[s] = (sentiments[s] || 0) + 1;
  });

  const dayMap = {};
  rows.forEach((r) => {
    const day = toIsoDay(r.timestamp);
    dayMap[day] = (dayMap[day] || 0) + 1;
  });

  return {
    kpis: { volume_conversations: total, escalades, fraudes, quality_moyenne: quality, conformite_moyenne: compliance },
    categories: Object.entries(categories).map(([label, count]) => ({ label, count })),
    sentiments: Object.entries(sentiments).map(([label, count]) => ({ label, count })),
    trends_7d: Object.entries(dayMap)
      .sort((a, b) => a[0].localeCompare(b[0]))
      .slice(-7)
      .map(([day, count]) => ({ day, count })),
  };
}

function plotAnalyticsCharts(rows) {
  if (!window.Plotly) return;

  analyticsChartIds.forEach((id) => {
    const chart = document.getElementById(id);
    if (chart) {
      if (window.Plotly?.purge) {
        try {
          window.Plotly.purge(chart);
        } catch (_err) {
          // Ignore purge errors and fall through to a hard reset.
        }
      }
      chart.innerHTML = '';
    }
  });

  const byDay = {};
  const fraudByDay = {};
  const dayHourMatrix = Array.from({ length: 7 }, () => Array.from({ length: 24 }, () => 0));

  rows.forEach((r) => {
    const day = toIsoDay(r.timestamp);
    byDay[day] = (byDay[day] || 0) + 1;

    if (r.is_fraud) {
      fraudByDay[day] = (fraudByDay[day] || 0) + 1;
    }

    const dt = new Date(r.timestamp);
    if (!Number.isNaN(dt.getTime())) {
      const weekDay = (dt.getDay() + 6) % 7;
      const hour = dt.getHours();
      dayHourMatrix[weekDay][hour] += 1;
    }
  });

  const dayKeys = Object.keys(byDay).sort();
  const dayCounts = dayKeys.map((d) => byDay[d]);

  Plotly.newPlot(
    'chartVolumeTimeline',
    [
      {
        x: dayKeys,
        y: dayCounts,
        type: 'scatter',
        mode: 'lines+markers',
        line: { color: '#0a3d91', width: 3 },
        marker: { color: '#2f8df7', size: 7 },
        name: 'Volume',
      },
    ],
    {
      margin: { t: 20, r: 10, b: 40, l: 40 },
      paper_bgcolor: 'rgba(0,0,0,0)',
      plot_bgcolor: 'rgba(0,0,0,0)',
      xaxis: { title: 'Jour' },
      yaxis: { title: 'Conversations' },
    },
    { responsive: true }
  );

  const heatmapHours = Array.from({ length: 24 }, (_v, i) => `${i}h`);
  const heatmapDays = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'];

  Plotly.newPlot(
    'chartActivityHeatmap',
    [
      {
        z: dayHourMatrix,
        x: heatmapHours,
        y: heatmapDays,
        type: 'heatmap',
        colorscale: [
          [0, '#e0f2fe'],
          [0.4, '#60a5fa'],
          [0.8, '#1d4ed8'],
          [1, '#172554'],
        ],
      },
    ],
    {
      margin: { t: 20, r: 10, b: 40, l: 40 },
      paper_bgcolor: 'rgba(0,0,0,0)',
      plot_bgcolor: 'rgba(0,0,0,0)',
      xaxis: { title: 'Heure' },
      yaxis: { title: 'Jour' },
    },
    { responsive: true }
  );

  const catMap = {};
  const sentMap = {};
  rows.forEach((r) => {
    const c = safeText(r.category || 'autre');
    const s = safeText(r.sentiment || 'neutral');
    catMap[c] = (catMap[c] || 0) + 1;
    sentMap[s] = (sentMap[s] || 0) + 1;
  });

  Plotly.newPlot(
    'chartCategoriesPie',
    [
      {
        labels: Object.keys(catMap),
        values: Object.values(catMap),
        type: 'pie',
        textinfo: 'label+percent',
        marker: { colors: ['#2563eb', '#0ea5e9', '#1d4ed8', '#3b82f6', '#60a5fa'] },
      },
    ],
    {
      margin: { t: 20, r: 10, b: 10, l: 10 },
      paper_bgcolor: 'rgba(0,0,0,0)',
    },
    { responsive: true }
  );

  Plotly.newPlot(
    'chartSentimentsDonut',
    [
      {
        labels: Object.keys(sentMap),
        values: Object.values(sentMap),
        type: 'pie',
        hole: 0.55,
      },
    ],
    {
      margin: { t: 20, r: 10, b: 10, l: 10 },
      paper_bgcolor: 'rgba(0,0,0,0)',
    },
    { responsive: true }
  );

  const fraudDays = Object.keys(fraudByDay).sort();
  const fraudCounts = fraudDays.map((d) => fraudByDay[d]);

  Plotly.newPlot(
    'chartFraudHistogram',
    [
      {
        x: fraudDays,
        y: fraudCounts,
        type: 'bar',
        marker: { color: '#dc2626' },
        name: 'Fraudes',
      },
    ],
    {
      margin: { t: 20, r: 10, b: 40, l: 40 },
      paper_bgcolor: 'rgba(0,0,0,0)',
      plot_bgcolor: 'rgba(0,0,0,0)',
      xaxis: { title: 'Jour' },
      yaxis: { title: 'Occurrences fraude' },
    },
    { responsive: true }
  );
}

function renderAnalyticsFromRows() {
  const summary = summarizeRows(filteredAnalyticsRows);
  const k = summary.kpis;

  analyticsKpis.innerHTML = `
    <div class="kpi-card kpi-blue"><div class="kpi-label">Conversations</div><div class="kpi-value">${k.volume_conversations || 0}</div></div>
    <div class="kpi-card kpi-orange"><div class="kpi-label">Escalades</div><div class="kpi-value">${k.escalades || 0}</div></div>
    <div class="kpi-card kpi-red"><div class="kpi-label">Fraudes</div><div class="kpi-value">${k.fraudes || 0}</div></div>
    <div class="kpi-card kpi-violet"><div class="kpi-label">Qualite</div><div class="kpi-value">${safeNum(k.quality_moyenne, 0).toFixed(1)}</div></div>
    <div class="kpi-card kpi-green"><div class="kpi-label">Conformite</div><div class="kpi-value">${safeNum(k.conformite_moyenne, 100).toFixed(1)}%</div></div>
  `;

  renderRows(analyticsCategories, summary.categories);
  renderRows(analyticsSentiments, summary.sentiments);
  renderRows(analyticsTrends, summary.trends_7d);
  plotAnalyticsCharts(filteredAnalyticsRows);
  runAnalyticsStagger();
}

async function loadAnalytics() {
  renderAnalyticsSkeleton();
  try {
    const res = await fetch('/web/analytics/data');
    if (!res.ok) throw new Error('analytics data error');
    const data = await res.json();
    analyticsRows = (data.rows || []).slice().sort((a, b) => safeText(a.timestamp).localeCompare(safeText(b.timestamp)));
    setupFilterOptions(analyticsRows);
    filteredAnalyticsRows = analyticsRows.slice();
    renderAnalyticsFromRows();
  } catch (_err) {
    analyticsKpis.innerHTML = '<div class="kpi-card">Impossible de charger les KPI.</div>';
  }
}

async function askAnalyticsChat(question) {
  const q = safeText(question).trim();
  if (!q) return;
  chatPush(analyticsChatHistory, 'user', q);
  analyticsChatInput.value = '';

  try {
    const res = await fetch('/web/analytics/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: q }),
    });
    if (!res.ok) throw new Error('analytics chat error');
    const data = await res.json();
    chatPush(analyticsChatHistory, 'assistant', safeText(data.answer));
  } catch (_err) {
    chatPush(analyticsChatHistory, 'assistant', 'Erreur temporaire du chat analytics.');
  }
}

function renderGovMetricRows(items) {
  const block = document.createElement('div');
  block.className = 'list-rows';
  items.forEach((it) => {
    const row = document.createElement('div');
    row.className = 'list-row';
    row.innerHTML = `<span>${safeText(it.label)}</span><strong>${safeText(it.value)}</strong>`;
    block.appendChild(row);
  });
  return block;
}

async function loadGovernance() {
  renderGovernanceSkeleton();
  try {
    const res = await fetch('/web/governance/summary');
    if (!res.ok) throw new Error('governance summary error');
    governanceData = await res.json();
    const data = governanceData;
    const e = data.evaluation || {};
    const o = data.observability || {};
    const dq = data.data_quality || {};

    govEvaluation.innerHTML = '<div class="mini-title">Evaluation Agent</div>';
    govEvaluation.appendChild(
      renderGovMetricRows([
        { label: 'Relevance Score', value: safeNum(e.relevance_score, 0).toFixed(1) },
        { label: 'Faithfulness Score', value: safeNum(e.faithfulness_score, 0).toFixed(1) },
        { label: 'Hallucination Rate', value: `${safeNum(e.hallucination_rate, 0).toFixed(1)}%` },
        { label: 'Compliance Score', value: `${safeNum(e.compliance_score, 0).toFixed(1)}%` },
        { label: 'Answer Quality', value: safeNum(e.answer_quality, 0).toFixed(1) },
      ])
    );

    govObservability.innerHTML = '<div class="mini-title">Observability (style Azure Monitor)</div>';
    govObservability.appendChild(
      renderGovMetricRows([
        { label: 'Temps de reponse moyen', value: `${safeNum(o.response_time_ms, 0).toFixed(0)} ms` },
        { label: 'Availability', value: `${safeNum(o.availability, 0).toFixed(1)}%` },
        { label: 'Quality Score', value: safeNum(o.quality_score, 0).toFixed(1) },
        { label: 'Traces', value: safeText(o.traces || 0) },
        { label: 'Alertes', value: (o.alerts || []).join(' | ') || 'Aucune' },
      ])
    );

    const logsTitle = document.createElement('div');
    logsTitle.className = 'mini-title mt-3';
    logsTitle.textContent = 'Logs recents';
    govObservability.appendChild(logsTitle);

    const logsRows = document.createElement('div');
    logsRows.className = 'list-rows';
    (data.logs || []).slice(0, 10).forEach((log) => {
      const row = document.createElement('div');
      row.className = 'list-row';
      row.innerHTML = `<span>${safeText(log.timestamp)} | ${safeText(log.agent)}</span><strong>${safeText(log.sentiment || 'neutral')}</strong>`;
      logsRows.appendChild(row);
    });
    govObservability.appendChild(logsRows);

    govDataQuality.innerHTML = '<div class="mini-title">Data Governance</div>';
    govDataQuality.appendChild(
      renderGovMetricRows([
        { label: 'Completeness', value: `${safeNum(dq.completeness, 0).toFixed(1)}%` },
        { label: 'Consistency', value: `${safeNum(dq.consistency, 0).toFixed(1)}%` },
        { label: 'Validity', value: `${safeNum(dq.validity, 0).toFixed(1)}%` },
        { label: 'Data Lineage', value: safeText(data.lineage || '') },
        { label: 'Compliance', value: safeText(data.compliance || '') },
        { label: 'Audit', value: safeText(data.audit || '') },
        { label: 'Privacy', value: safeText(data.privacy || '') },
      ])
    );
  } catch (_err) {
    govEvaluation.textContent = 'Impossible de charger les donnees de gouvernance.';
    govObservability.textContent = 'Impossible de charger les donnees d observabilite.';
    govDataQuality.textContent = 'Impossible de charger les donnees de data quality.';
  }
}

async function askGovernanceChat(question) {
  const q = safeText(question).trim();
  if (!q) return;
  chatPush(governanceChatHistory, 'user', q);
  governanceChatInput.value = '';

  try {
    const res = await fetch('/web/governance/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: q }),
    });
    if (!res.ok) throw new Error('governance chat error');
    const data = await res.json();
    chatPush(governanceChatHistory, 'assistant', safeText(data.answer));
  } catch (_err) {
    chatPush(governanceChatHistory, 'assistant', 'Erreur temporaire du chat governance.');
  }
}

function switchSpace(space, roleLabel) {
  if (space === activeSpace) return;

  if (spaceTransitionTimer) {
    clearTimeout(spaceTransitionTimer);
  }

  const currentScreen = document.getElementById(`space-${activeSpace}`);
  const nextScreen = document.getElementById(`space-${space}`);

  if (currentScreen) {
    currentScreen.classList.add('space-exit');
  }

  if (nextScreen) {
    nextScreen.classList.add('active', 'space-enter');
  }

  spaceTransitionTimer = window.setTimeout(() => {
    if (currentScreen) {
      currentScreen.classList.remove('active', 'space-exit');
    }
    if (nextScreen) {
      nextScreen.classList.remove('space-enter');
    }
  }, 180);

  activeSpace = space;
  spaceButtons.forEach((b) => b.classList.toggle('active', b.dataset.space === space));
  activeRoleLabel.textContent = roleLabel;
  if (customerQuickBlock) {
    customerQuickBlock.style.display = space === 'customer' ? 'block' : 'none';
  }

  if (space === 'analytics') {
    analyticsChatHistory.innerHTML = '';
    loadAnalytics();
  }

  if (space === 'governance') {
    governanceChatHistory.innerHTML = '';
    loadGovernance();
  }
}

function setupRealtimeRefresh() {
  if (realtimeTimer) {
    clearInterval(realtimeTimer);
  }

  realtimeTimer = setInterval(() => {
    if (activeSpace === 'analytics') {
      loadAnalytics();
    }
    if (activeSpace === 'governance') {
      loadGovernance();
    }
  }, 15000);
}

chatForm.addEventListener('submit', (e) => {
  e.preventDefault();
  sendCustomerMessage(chatInput.value);
});

quickButtons.forEach((btn) => {
  btn.addEventListener('click', () => {
    sendCustomerMessage(btn.dataset.question || btn.textContent || '');
  });
});

premiumQuickButtons.forEach((btn) => {
  btn.addEventListener('click', () => {
    const question = btn.dataset.question || btn.textContent || '';
    if (!question) return;

    btn.classList.add('is-used');
    btn.disabled = true;
    sendCustomerMessage(question);
  });
});

spaceButtons.forEach((btn) => {
  btn.addEventListener('click', () => {
    switchSpace(btn.dataset.space, btn.dataset.role || 'Utilisateur');
  });
});

govTabButtons.forEach((btn) => {
  btn.addEventListener('click', () => {
    govTabButtons.forEach((b) => b.classList.toggle('active', b === btn));
    const tab = btn.dataset.govTab;
    govEvaluation.classList.toggle('active', tab === 'evaluation');
    govObservability.classList.toggle('active', tab === 'observability');
    govDataQuality.classList.toggle('active', tab === 'dataquality');
  });
});

analyticsChatForm.addEventListener('submit', (e) => {
  e.preventDefault();
  askAnalyticsChat(analyticsChatInput.value);
});

analyticsPromptChips.forEach((btn) => {
  btn.addEventListener('click', () => {
    askAnalyticsChat(btn.dataset.q || btn.textContent || '');
  });
});

governanceChatForm.addEventListener('submit', (e) => {
  e.preventDefault();
  askGovernanceChat(governanceChatInput.value);
});

applyFiltersBtn.addEventListener('click', () => {
  applyFilters();
});

resetFiltersBtn.addEventListener('click', () => {
  filterStartDate.value = '';
  filterEndDate.value = '';
  filterCategory.value = 'all';
  filterSentiment.value = 'all';
  filterAgent.value = 'all';
  filteredAnalyticsRows = analyticsRows.slice();
  renderAnalyticsFromRows();
});

exportAnalyticsCsvBtn.addEventListener('click', () => {
  downloadBlob('analytics_export.csv', toCsv(filteredAnalyticsRows), 'text/csv;charset=utf-8;');
});

exportAnalyticsPdfBtn.addEventListener('click', () => {
  exportPdf('Analytics Report', filteredAnalyticsRows);
});

exportGovernanceCsvBtn.addEventListener('click', () => {
  const rows = governanceData?.logs || [];
  downloadBlob('governance_export.csv', toCsv(rows), 'text/csv;charset=utf-8;');
});

exportGovernancePdfBtn.addEventListener('click', () => {
  const rows = governanceData?.logs || [];
  exportPdf('Governance Report', rows);
});

addCustomerMessage('assistant', `Bonjour et bienvenue sur AELON.

Je suis votre assistant bancaire basé sur l'intelligence artificielle.

Je peux vous accompagner dans les demandes courantes liées à :
• cartes bancaires
• virements
• accès au compte
• opérations quotidiennes

🔒 Vos données sensibles sont protégées.

⚠️ Pour les situations nécessitant une intervention humaine, un conseiller pourra prendre le relais.

Comment puis-je vous aider aujourd'hui ?`);
switchSpace('customer', 'Client bancaire');
setupRealtimeRefresh();
initTheme();

if (themeToggleBtn) {
  themeToggleBtn.addEventListener('click', () => {
    const privateMode = !document.body.classList.contains('private-theme');
    setTheme(privateMode);
    localStorage.setItem('aelon-theme', privateMode ? 'private' : 'default');
  });
}
