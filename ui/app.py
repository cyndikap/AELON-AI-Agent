# -*- coding: utf-8 -*-

# ================= IMPORTS =================

import sys
import json
import html
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from datetime import datetime
import streamlit as st


from azure_chat_llm import AzureChatLLM
from multi_agent.fraud.fraud_agent import FraudAgent
from multi_agent.l0.l0_agent import L0Agent
from multi_agent.l1.l1_agent import L1Agent
from multi_agent.sentiment.sentiment_agent import SentimentAgent
from multi_agent.compliance.compliance_agent import ComplianceAgent
from multi_agent.orchestrator import Orchestrator
from utils.category_detector import detect_category, CATEGORY_COLORS, CATEGORY_ICONS
from utils.export_handler import to_csv_string





# ================= CONFIG =================
st.set_page_config(page_title="AELON", page_icon="🤖", layout="wide")
st.markdown("""
<style>

/* ===== GLOBAL ===== */
html, body, .stApp {
    background-color: #F5F7FA;
    color: #1F2937;
    font-family: 'Inter', sans-serif;
}

/* ===== SIDEBAR ===== */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #071629 0%, #0B2447 100%);
    border-right: 1px solid #16355F;
}

section[data-testid="stSidebar"] * {
    color: #F8FAFC !important;
}

.sidebar-brand {
    text-align: center;
    padding: 12px 8px 6px 8px;
}

.sidebar-avatar {
    width: 86px;
    height: 86px;
    border-radius: 50%;
    object-fit: cover;
    border: 2px solid #2C6CA6;
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.3);
}

.sidebar-title {
    margin-top: 10px;
    font-size: 1.25rem;
    font-weight: 700;
    letter-spacing: 0.4px;
}

.sidebar-subtitle {
    margin-top: 2px;
    font-size: 0.82rem;
    color: #C7D2FE !important;
}

.sidebar-section {
    margin-top: 8px;
    margin-bottom: 4px;
    font-size: 0.82rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #93C5FD !important;
}

.sidebar-sep {
    border: 0;
    border-top: 1px solid rgba(147, 197, 253, 0.25);
    margin: 10px 0 12px 0;
}

.sidebar-info {
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(147, 197, 253, 0.22);
    border-radius: 10px;
    padding: 10px 12px;
    margin-bottom: 8px;
    font-size: 0.92rem;
}

.sidebar-footer {
    text-align: center;
    font-size: 0.78rem;
    color: #CBD5E1 !important;
    margin-top: 8px;
    margin-bottom: 4px;
}

/* ===== TITRES ===== */
h1, h2, h3 {
    color: #1F2937;
}

/* ===== INPUT ===== */
input, textarea {
    background-color: #FFFFFF !important;
    color: #1F2937 !important;
    border-radius: 10px !important;
    border: 1px solid #E5E7EB !important;
}

/* ===== SELECTBOX ===== */
div[data-baseweb="select"] {
    background-color: #FFFFFF !important;
    border: 1px solid #E5E7EB !important;
    border-radius: 10px !important;
}

div[data-baseweb="select"] div,
div[data-baseweb="select"] span,
div[data-baseweb="select"] input {
    color: #1F2937 !important;
}

/* ===== DROPDOWN ===== */
div[role="listbox"] {
    background-color: #FFFFFF !important;
}

div[role="option"] {
    color: #1F2937 !important;
}

div[role="option"]:hover {
    background-color: #EEF2FF !important;
}

/* ===== BUTTON ===== */
button {
    background: linear-gradient(135deg, #3B82F6, #06B6D4) !important;
    color: white !important;
    border-radius: 10px !important;
    border: none !important;
}

/* ===== CARD STYLE ===== */
.card {
    background: #FFFFFF;
    border-radius: 14px;
    padding: 1rem;
    border: 1px solid #E5E7EB;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}

/* ===== METRIC ===== */
[data-testid="stMetric"] {
    background: #FFFFFF;
    padding: 15px;
    border-radius: 12px;
    border: 1px solid #E5E7EB;
}

/* ===== CHART ===== */
.vega-embed text {
    fill: #1F2937 !important;
}

/* ===== CHAT ===== */
[data-testid="stChatInput"] textarea {
    background: #FFFFFF !important;
    color: #1F2937 !important;
}

[data-testid="chatAvatarIcon-assistant"] {
    background: linear-gradient(135deg, #facc15, #fbbf24) !important;
    border-radius: 14px !important;
    padding: 10px !important;
    box-shadow: 0 4px 12px rgba(250, 204, 21, 0.6) !important;
}

.chat-header {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 8px;
    margin-top: 6px;
    margin-bottom: 14px;
}

.chat-header-avatar {
    width: 78px;
    height: 78px;
    border-radius: 50%;
    border: 2px solid #f4d165;
    box-shadow: 0 10px 24px rgba(252, 211, 77, 0.28);
}

.chat-header-title {
    font-size: 1.3rem;
    font-weight: 700;
    color: #eef2ff;
    letter-spacing: 0.02em;
}

[data-testid="stChatMessage"] {
    margin-bottom: 0.45rem;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

[data-testid="stChatMessage"] [data-testid="stChatMessageAvatar"],
[data-testid="stChatMessage"] [data-testid="stChatMessageAvatarUser"],
[data-testid="stChatMessage"] [data-testid="stChatMessageAvatarAssistant"] {
    width: 2.35rem !important;
    height: 2.35rem !important;
    min-width: 2.35rem !important;
    min-height: 2.35rem !important;
    flex: 0 0 2.35rem !important;
}

[data-testid="stChatMessage"] [data-testid="stChatMessageAvatar"] img,
[data-testid="stChatMessage"] [data-testid="stChatMessageAvatar"] svg,
[data-testid="stChatMessage"] [data-testid="stChatMessageAvatarUser"] img,
[data-testid="stChatMessage"] [data-testid="stChatMessageAvatarUser"] svg,
[data-testid="stChatMessage"] [data-testid="stChatMessageAvatarAssistant"] img,
[data-testid="stChatMessage"] [data-testid="stChatMessageAvatarAssistant"] svg {
    width: 100% !important;
    height: 100% !important;
    border-radius: 50% !important;
    object-fit: cover !important;
}

[data-testid="stChatMessage"] [data-testid="stChatMessageContent"] {
    position: relative;
    max-width: min(78%, 760px);
    border-radius: 18px;
    padding: 0.7rem 0.9rem;
    transition: transform 0.28s ease, opacity 0.28s ease, box-shadow 0.28s ease;
    box-shadow: 0 10px 20px rgba(2, 8, 23, 0.16);
}

/* Neutralise le fond natif pour laisser les bulles custom visibles */
[data-testid="stChatMessage"] [data-testid="stChatMessageContent"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
}

[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"],
[data-testid="stChatMessage"] [data-testid="stElementContainer"],
[data-testid="stChatMessage"] [data-testid="stVerticalBlock"],
[data-testid="stChatMessage"] [data-testid="stHorizontalBlock"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

.aelon-bubble {
    position: relative;
    display: inline-block;
    width: fit-content;
    max-width: min(78%, 760px);
    padding: 0.72rem 0.95rem;
    border-radius: 18px;
    box-shadow: 0 12px 24px rgba(2, 8, 23, 0.18);
    transition: transform 0.28s ease, opacity 0.28s ease, box-shadow 0.28s ease;
    line-height: 1.45;
    word-wrap: break-word;
}

.aelon-bubble-wrap {
    width: fit-content;
    max-width: 100%;
    display: flex;
}

.aelon-bubble-wrap-user {
    justify-content: flex-end;
    margin-left: auto;
}

.aelon-bubble-wrap-assistant {
    justify-content: flex-start;
    margin-right: auto;
}

.aelon-bubble-user {
    background: #2563EB;
    border: 1px solid #1D4ED8;
    color: #FFFFFF;
    border-radius: 18px 4px 18px 18px;
    animation: fadeSlideInRight 0.36s ease both;
}

.aelon-bubble-user::after {
    content: "";
    position: absolute;
    right: -9px;
    bottom: 10px;
    width: 0;
    height: 0;
    border-left: 10px solid #2563EB;
    border-top: 8px solid transparent;
    border-bottom: 8px solid transparent;
}

.aelon-bubble-assistant {
    background: #FDE68A;
    border: 1px solid #F5C84B;
    color: #1F2937;
    border-radius: 4px 18px 18px 18px;
    box-shadow: 0 0 0 1px rgba(245, 200, 75, 0.15), 0 8px 20px rgba(245, 200, 75, 0.32);
    animation: fadeSlideInLeft 0.36s ease both;
}

.aelon-bubble-assistant::before {
    content: "";
    position: absolute;
    left: -9px;
    bottom: 10px;
    width: 0;
    height: 0;
    border-right: 10px solid #FDE68A;
    border-top: 8px solid transparent;
    border-bottom: 8px solid transparent;
}

.aelon-bubble p {
    margin: 0;
}

.aelon-bubble * {
    color: inherit !important;
    background: transparent !important;
}

@keyframes fadeSlideInLeft {
    from {
        opacity: 0;
        transform: translateX(-18px) translateY(2px);
    }
    to {
        opacity: 1;
        transform: translateX(0) translateY(0);
    }
}

@keyframes fadeSlideInRight {
    from {
        opacity: 0;
        transform: translateX(18px) translateY(2px);
    }
    to {
        opacity: 1;
        transform: translateX(0) translateY(0);
    }
}

/* ===== CHAT MESSAGES — User (right) ===== */
[data-testid="stChatMessage"]:has(.aelon-bubble-user) {
    flex-direction: row-reverse !important;
    justify-content: flex-end !important;
    text-align: right !important;
   gap: 0rem
}

/* Avatar utilisateur: forcer bleu (pas rouge) */
[data-testid="stChatMessage"]:has(.aelon-bubble-user) [data-testid="stChatMessageAvatar"],
[data-testid="stChatMessage"]:has(.aelon-bubble-user) [data-testid="stChatMessageAvatarUser"],
[data-testid="stChatMessage"][aria-label*="user" i] [data-testid="stChatMessageAvatar"],
[data-testid="stChatMessage"][aria-label*="user" i] [data-testid="stChatMessageAvatarUser"] {
    background: #2563EB !important;
    border: 2px solid #1D4ED8 !important;
    color: #FFFFFF !important;
}

[data-testid="stChatMessage"]:has(.aelon-bubble-user) [data-testid="stChatMessageAvatar"] svg,
[data-testid="stChatMessage"]:has(.aelon-bubble-user) [data-testid="stChatMessageAvatarUser"] svg,
[data-testid="stChatMessage"][aria-label*="user" i] [data-testid="stChatMessageAvatar"] svg,
[data-testid="stChatMessage"][aria-label*="user" i] [data-testid="stChatMessageAvatarUser"] svg {
    fill: #FFFFFF !important;
    color: #FFFFFF !important;
    stroke: #FFFFFF !important;
}

[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]),
[data-testid="stChatMessage"][aria-label*="user" i] {
    flex-direction: row-reverse !important;
    justify-content: flex-end !important;
    text-align: right !important;
    gap: 0rem !important;
    animation: fadeSlideInRight 0.36s ease both;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"])
    [data-testid="stChatMessageContent"],
[data-testid="stChatMessage"][aria-label*="user" i]
    [data-testid="stChatMessageContent"] {
    background: #2563EB !important;
    border: 1px solid #1D4ED8 !important;
    border-radius: 18px 4px 18px 18px !important;
    color: #FFFFFF !important;
    display: inline-block;
    width: fit-content;
    max-width: min(78%, 760px);
    margin-left: auto;
    box-shadow: 0 12px 24px rgba(37, 99, 235, 0.35);
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"])
    [data-testid="stChatMessageContent"]::after,
[data-testid="stChatMessage"][aria-label*="user" i]
    [data-testid="stChatMessageContent"]::after {
    content: "";
    position: absolute;
    right: -9px;
    bottom: 10px;
    width: 0;
    height: 0;
    border-left: 10px solid #2563EB;
    border-top: 8px solid transparent;
    border-bottom: 8px solid transparent;
}

/* ===== CHAT MESSAGES — Assistant (yellow) ===== */
[data-testid="stChatMessage"]:has(.aelon-bubble-assistant) {
    flex-direction: row !important;
    justify-content: flex-start !important;
    text-align: left !important;
    gap: 0rem !important;
}

[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]),
[data-testid="stChatMessage"][aria-label*="assistant" i] {
    justify-content: flex-start !important;
    gap: 0rem !important;
    animation: fadeSlideInLeft 0.36s ease both;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"])
    [data-testid="stChatMessageContent"],
[data-testid="stChatMessage"][aria-label*="assistant" i]
    [data-testid="stChatMessageContent"] {
    background: #FDE68A !important;
    border: 1px solid #F5C84B !important;
    border-radius: 3px 18px 18px 18px !important;
    color: #1F2937 !important;
    display: inline-block;
    width: fit-content;
    max-width: min(78%, 760px);
    box-shadow: 0 0 0 1px rgba(245, 200, 75, 0.15), 0 8px 20px rgba(245, 200, 75, 0.32);
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"])
    [data-testid="stChatMessageContent"]::before,
[data-testid="stChatMessage"][aria-label*="assistant" i]
    [data-testid="stChatMessageContent"]::before {
    content: "";
    position: absolute;
    left: -9px;
    bottom: 10px;
    width: 0;
    height: 0;
    border-right: 10px solid #FDE68A;
    border-top: 8px solid transparent;
    border-bottom: 8px solid transparent;
}

[data-testid="stSidebar"] [role="radiogroup"] {
    gap: 0.35rem;
}

[data-testid="stSidebar"] [role="radio"] {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(147, 197, 253, 0.28);
    border-radius: 10px;
    padding: 0.45rem 0.55rem;
}

[data-testid="stSidebar"] [role="radio"][aria-checked="true"] {
    background: rgba(59, 130, 246, 0.22);
    border-color: #60A5FA;
}

</style>
""", unsafe_allow_html=True)


# ================= CSS FIX =================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body {
    background: #071629;
    color: #eef2ff;
    font-family: 'Inter', sans-serif;
}

/* Fix dropdown visibility */
div[data-baseweb="select"] div,
div[data-baseweb="select"] span,
div[data-baseweb="select"] input {
    color: #ffffff !important;
}

div[role="option"] {
    color: white !important;
}
</style>
""", unsafe_allow_html=True)



# ================= INIT AGENTS =================
@st.cache_resource
def init_agents():
    llm = AzureChatLLM()
    KB_PATH = Path(__file__).resolve().parent.parent / "knowledge_base" / "it_support_kb.md"

    return (
        FraudAgent(llm),
        SentimentAgent(llm),
        ComplianceAgent(llm),
        L0Agent(llm, KB_PATH),
        L1Agent(llm)
    )

fraud_agent, sentiment_agent, compliance_agent, l0_agent, l1_agent = init_agents()
orchestrator = Orchestrator()


# ================= SIDEBAR =================
with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <img class="sidebar-avatar" src="https://cdn-icons-png.flaticon.com/512/4712/4712100.png" alt="AELON Avatar" />
            <div class="sidebar-title">AELON</div>
            <div class="sidebar-subtitle">Banking Assistant</div>
        </div>
        <hr class="sidebar-sep" />
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="sidebar-section">Navigation</div>', unsafe_allow_html=True)
    nav_choice = st.radio(
        "Choisissez une vue",
        ["💬 Chat Assistant", "📊 Dashboard Admin"],
        label_visibility="collapsed",
    )
    mode = "Utilisateur" if nav_choice == "💬 Chat Assistant" else "Admin"

    st.markdown('<hr class="sidebar-sep" />', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-section">Informations</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-info">Ne partagez jamais vos identifiants</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-info">Vérifiez vos transactions</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-info">📞 Contacter le support en cas de doute</div>', unsafe_allow_html=True)

    st.markdown('<hr class="sidebar-sep" />', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-section"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-footer">© AELON - 2026</div>', unsafe_allow_html=True)

# ================= STORAGE =================
INTERACTIONS_FILE = "interactions.json"

def load_data():
    if Path(INTERACTIONS_FILE).exists():
        return json.load(open(INTERACTIONS_FILE))
    return []

def save_data(data):
    json.dump(data, open(INTERACTIONS_FILE, "w"), indent=2)


def render_chat_bubble(role: str, content: str) -> None:
    """Render chat content with stable custom bubbles independent of Streamlit internals."""
    bubble_class = "aelon-bubble-user" if role == "user" else "aelon-bubble-assistant"
    wrap_class = "aelon-bubble-wrap-user" if role == "user" else "aelon-bubble-wrap-assistant"
    safe_content = html.escape(str(content)).replace("\n", "<br>")
    st.markdown(
        (
            f'<div class="aelon-bubble-wrap {wrap_class}">'
            f'<div class="aelon-bubble {bubble_class}">{safe_content}</div>'
            f'</div>'
        ),
        unsafe_allow_html=True,
    )

# ================= ADMIN =================
if mode == "Admin":
    import pandas as pd
    import altair as alt

    st.title("📊 Dashboard Admin — AELON Analytics")

    data = load_data()

    if not data:
        st.warning("⚠️ Pas de données disponibles. Lancez quelques conversations en mode Utilisateur d'abord.")
        st.stop()

    df = pd.DataFrame(data)

    # ── Ensure required columns exist (backward compat with old records) ──
    if "category" not in df.columns:
        df["category"] = df["query"].apply(detect_category) if "query" in df.columns else "autre"
    else:
        df["category"] = df["category"].fillna("autre")
        # Re-detect for records that were saved without a category
        mask = df["category"].isin(["", "autre"])
        if "query" in df.columns:
            df.loc[mask, "category"] = df.loc[mask, "query"].apply(detect_category)

    if "escalated" not in df.columns:
        df["escalated"] = df["agent"].apply(lambda x: x == "L1") if "agent" in df.columns else False
    df["escalated"] = df["escalated"].fillna(False).astype(bool)

    if "fraud_score" not in df.columns:
        df["fraud_score"] = 0
    df["fraud_score"] = pd.to_numeric(df["fraud_score"], errors="coerce").fillna(0)

    if "sentiment" not in df.columns:
        df["sentiment"] = "neutre"
    df["sentiment"] = df["sentiment"].fillna("neutre")

    if "agent" not in df.columns:
        df["agent"] = "L0"
    df["agent"] = df["agent"].fillna("L0")

    if "risk_level" not in df.columns:
        df["risk_level"] = "LOW"

    df["timestamp"] = pd.to_datetime(
        df["timestamp"] if "timestamp" in df.columns else pd.Series(dtype=str),
        errors="coerce",
    )

    # ── SIDEBAR FILTERS ──────────────────────────────────────────────────
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔍 Filtres Dashboard")

    categories_opts = ["Toutes"] + sorted(df["category"].unique().tolist())
    sel_category = st.sidebar.selectbox("Catégorie", categories_opts)

    agents_opts = ["Tous"] + sorted(df["agent"].unique().tolist())
    sel_agent = st.sidebar.selectbox("Agent", agents_opts)

    valid_dates = df["timestamp"].dropna()
    if len(valid_dates) > 0:
        min_date = valid_dates.min().date()
        max_date = valid_dates.max().date()
        date_range = st.sidebar.date_input(
            "Période", value=(min_date, max_date),
            min_value=min_date, max_value=max_date
        )
    else:
        date_range = None

    # ── Apply filters ────────────────────────────────────────────────────
    filtered = df.copy()
    if sel_category != "Toutes":
        filtered = filtered[filtered["category"] == sel_category]
    if sel_agent != "Tous":
        filtered = filtered[filtered["agent"] == sel_agent]
    if date_range and len(date_range) == 2:
        filtered = filtered[
            (filtered["timestamp"].dt.date >= date_range[0]) &
            (filtered["timestamp"].dt.date <= date_range[1])
        ]

    total = len(filtered)

    # ── KPIs ─────────────────────────────────────────────────────────────
    st.subheader("📈 Indicateurs Clés")
    k1, k2, k3, k4 = st.columns(4)

    n_escalated = int(filtered["escalated"].sum())
    escalation_rate = (n_escalated / total * 100) if total > 0 else 0
    avg_fraud = float(filtered["fraud_score"].mean()) if total > 0 else 0
    top_cat = filtered["category"].mode()[0] if total > 0 else "N/A"
    top_icon = CATEGORY_ICONS.get(top_cat, "❓")

    k1.metric("📊 Interactions", total)
    k2.metric("🔄 Taux d'escalade", f"{escalation_rate:.1f}%",
              delta=f"{n_escalated} escalades")
    k3.metric("⚠️ Score fraude moyen", f"{avg_fraud:.1f}")
    k4.metric("🏆 Catégorie principale", f"{top_icon} {top_cat.capitalize()}")

    st.markdown("---")

    # ── CHARTS ───────────────────────────────────────────────────────────
    st.subheader("📊 Visualisations")

    chart_col1, chart_col2 = st.columns(2)

    # Category distribution (pie)
    with chart_col1:
        st.markdown("**Distribution par catégorie**")
        if total > 0:
            cat_counts = (
                filtered["category"].value_counts()
                .reset_index()
            )
            cat_counts.columns = ["category", "count"]
            cat_counts["color"] = cat_counts["category"].map(CATEGORY_COLORS).fillna("#6B7280")
            pie = (
                alt.Chart(cat_counts)
                .mark_arc(outerRadius=110)
                .encode(
                    theta=alt.Theta("count:Q"),
                    color=alt.Color(
                        "category:N",
                        scale=alt.Scale(
                            domain=list(CATEGORY_COLORS.keys()),
                            range=list(CATEGORY_COLORS.values()),
                        ),
                        legend=alt.Legend(title="Catégorie"),
                    ),
                    tooltip=["category:N", "count:Q"],
                )
                .properties(height=250)
            )
            st.altair_chart(pie, use_container_width=True)
        else:
            st.info("Aucune donnée après filtrage.")

    # Agent distribution (bar)
    with chart_col2:
        st.markdown("**Répartition L0 / L1**")
        if total > 0:
            agent_counts = (
                filtered["agent"].value_counts()
                .reset_index()
            )
            agent_counts.columns = ["agent", "count"]
            bar_agent = (
                alt.Chart(agent_counts)
                .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
                .encode(
                    x=alt.X("agent:N", axis=alt.Axis(labelAngle=0), title="Agent"),
                    y=alt.Y("count:Q", title="Nombre"),
                    color=alt.Color(
                        "agent:N",
                        scale=alt.Scale(
                            domain=["L0", "L1", "blocked"],
                            range=["#3B82F6", "#10B981", "#EF4444"],
                        ),
                        legend=None,
                    ),
                    tooltip=["agent:N", "count:Q"],
                )
                .properties(height=250)
            )
            st.altair_chart(bar_agent, use_container_width=True)
        else:
            st.info("Aucune donnée après filtrage.")

    chart_col3, chart_col4 = st.columns(2)

    # Fraud score histogram
    with chart_col3:
        st.markdown("**Distribution des scores de fraude**")
        if total > 0 and filtered["fraud_score"].sum() > 0:
            hist = (
                alt.Chart(filtered[["fraud_score"]].dropna())
                .mark_bar(color="#EF4444", cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
                .encode(
                    x=alt.X("fraud_score:Q", bin=alt.Bin(maxbins=10), title="Score"),
                    y=alt.Y("count():Q", title="Fréquence"),
                    tooltip=["count():Q"],
                )
                .properties(height=230)
            )
            st.altair_chart(hist, use_container_width=True)
        else:
            st.info("Scores de fraude tous à 0 ou aucune donnée.")

    # Sentiment distribution
    with chart_col4:
        st.markdown("**Répartition des sentiments**")
        if total > 0:
            sent_counts = (
                filtered["sentiment"].value_counts()
                .reset_index()
            )
            sent_counts.columns = ["sentiment", "count"]
            bar_sent = (
                alt.Chart(sent_counts)
                .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
                .encode(
                    x=alt.X("sentiment:N", axis=alt.Axis(labelAngle=-20), title="Sentiment"),
                    y=alt.Y("count:Q", title="Nombre"),
                    color=alt.Color(
                        "sentiment:N",
                        scale=alt.Scale(scheme="tableau10"),
                        legend=None,
                    ),
                    tooltip=["sentiment:N", "count:Q"],
                )
                .properties(height=230)
            )
            st.altair_chart(bar_sent, use_container_width=True)
        else:
            st.info("Aucune donnée après filtrage.")

    st.markdown("---")

    # ── BUSINESS INSIGHTS ────────────────────────────────────────────────
    st.subheader("💡 Insights Métier")

    ins_col1, ins_col2, ins_col3 = st.columns(3)

    with ins_col1:
        st.markdown("**🔁 Problèmes récurrents**")
        if "query" in filtered.columns and total > 0:
            top_queries = filtered["query"].value_counts().head(3)
            for q, cnt in top_queries.items():
                display_q = str(q)[:60] + ("..." if len(str(q)) > 60 else "")
                st.markdown(f"- *{display_q}* — **{cnt}x**")
        else:
            st.info("Pas de données.")

    with ins_col2:
        st.markdown("**📂 Catégories les plus fréquentes**")
        if total > 0:
            for cat, cnt in filtered["category"].value_counts().head(5).items():
                icon = CATEGORY_ICONS.get(str(cat), "❓")
                pct = cnt / total * 100
                st.markdown(f"{icon} **{str(cat).capitalize()}** — {cnt} ({pct:.0f}%)")

    with ins_col3:
        st.markdown("**⚡ Taux de résolution**")
        if total > 0:
            fraud_blocked = int((filtered["agent"] == "blocked").sum()) if "agent" in filtered.columns else 0
            resolved = total - fraud_blocked
            st.markdown(f" Résolus : **{resolved}** ({resolved/total*100:.0f}%)")
            st.markdown(f"🔄 Escaladés L1 : **{n_escalated}** ({escalation_rate:.1f}%)")
            st.markdown(f"🚨 Bloqués (fraude) : **{fraud_blocked}**")

    st.markdown("---")

    # ── DATA TABLE ───────────────────────────────────────────────────────
    st.subheader("📋 Historique des interactions")

    display_cols = [c for c in ["timestamp", "category", "query", "agent",
                                "escalated", "fraud_score", "risk_level",
                                "sentiment", "resolution_status"]
                    if c in filtered.columns]
    st.dataframe(filtered[display_cols].sort_values("timestamp", ascending=False),
                 use_container_width=True, height=300)

    # ── CSV EXPORT ───────────────────────────────────────────────────────
    st.markdown("---")
    export_data = filtered.copy()
    export_data["timestamp"] = export_data["timestamp"].astype(str)
    csv_content = to_csv_string(export_data.to_dict(orient="records"))
    st.download_button(
        label="📥 Exporter les interactions (CSV)",
        data=csv_content,
        file_name=f"aelon_interactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        use_container_width=True,
    )

# ================= USER =================
else:

    # ===== SESSION CHAT =====
    if "messages" not in st.session_state:
        st.session_state.messages = []

        #  message de bienvenue
        st.session_state.messages.append({
            "role": "assistant",
            "content": "👋 Bonjour, je suis AELON, votre assistant bancaire.\n\nComment puis-je vous aider aujourd’hui ?"
        })

        #  message sécurité
        st.session_state.messages.append({
            "role": "assistant",
            "content": "🔐 **Important :** Ne partagez jamais vos informations sensibles (mot de passe, code OTP, numéro de carte)."
        })

    # ===== HEADER =====
    st.markdown("""
        <style>
        .stApp {
            background-color: #0b1e3b;
            color: white;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown(
        """
        <div class="chat-header">
            <img class="chat-header-avatar" src="https://cdn-icons-png.flaticon.com/512/4712/4712100.png" alt="AELON - Banking Assistant" />
            <div class="chat-header-title">AELON - Banking Assistant</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")


    # ===== CHAT HISTORY =====
    for msg in st.session_state.messages:
        if msg["role"] == "assistant":
            with st.chat_message("assistant", avatar="🤖"):
                render_chat_bubble(msg["role"], msg["content"])
        else:
            with st.chat_message(msg["role"]):
                render_chat_bubble(msg["role"], msg["content"])

    # ===== INPUT =====
    user_input = st.chat_input("Écrivez votre message...")

    if user_input:
        # Affichage immédiat du message utilisateur + persistance dans l'historique.
        with st.chat_message("user"):
            render_chat_bubble("user", user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})

    # ===== TRAITEMENT =====
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":

        user_query = st.session_state.messages[-1]["content"]

        # ===== FRAUD =====
        fraud_result = fraud_agent.analyze(user_query)

        if fraud_result["is_fraud"]:
            response = "🚨 Message suspect détecté. Veuillez contacter le support."
            agent_used = "blocked"
            escalated = False
            escalation_reason = None
            sentiment_value = "neutre"

        else:
            # ===== ORCHESTRATOR =====
            with st.spinner("AELON réfléchit..."):
                orch_result = orchestrator.handle_user_query(user_query)

            if isinstance(orch_result, dict):
                response      = orch_result.get("response", "")
                escalated     = orch_result.get("escalated", False)
                escalation_reason = orch_result.get("escalation_reason")
                agent_used    = orch_result.get("agent", "L0")
                sentiment_value = orch_result.get("sentiment", "neutre")
            else:
                response          = str(orch_result)
                escalated         = False
                escalation_reason = None
                agent_used        = "L0"
                sentiment_value   = "neutre"

            # ── Intermediate escalation message ──────────────────────────
            if escalated:
                escalation_msg = (
                    "🔄 Je transmets votre demande à un conseiller."
                )
                with st.chat_message("assistant", avatar="🤖"):
                    render_chat_bubble("assistant", escalation_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": escalation_msg
                })

        # ===== AFFICHAGE =====
        with st.chat_message("assistant", avatar="🤖"):
            render_chat_bubble("assistant", response)

        st.session_state.messages.append({
            "role": "assistant",
            "content": response
        })

        # ===== LOG DATA =====
        record = {
            "timestamp":         datetime.now().isoformat(),
            "query":             user_query,
            "query_length":      len(user_query),
            "category":          detect_category(user_query),
            "fraud_score":       fraud_result["score"],
            "risk_level":        fraud_result["risk_level"],
            "is_fraud":          fraud_result["is_fraud"],
            "agent":             agent_used,
            "escalated":         escalated,
            "escalation_reason": escalation_reason,
            "response_preview":  response[:100],
            "sentiment":         sentiment_value,
            "resolution_status": "fraud_blocked" if fraud_result["is_fraud"] else "resolved",
        }

        data = load_data()
        data.append(record)
        save_data(data)