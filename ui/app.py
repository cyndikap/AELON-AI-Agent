# -*- coding: utf-8 -*-

# ================= IMPORTS =================

import sys
import json
import html
import re
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
from utils.category_detector import detect_category, get_category_label
from utils.export_handler import interactions_to_csv





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
    background-color: #FFFFFF;
    border-right: 1px solid #E5E7EB;
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

/* ===== CHAT INPUT ===== */
[data-testid="stChatInput"] textarea {
    background: #FFFFFF !important;
    color: #1F2937 !important;
}

/* ===== CUSTOM CHAT BUBBLES ===== */
.chat-container {
    display: flex;
    flex-direction: column;
    gap: 12px;
    padding: 8px 0;
}

.msg-row {
    display: flex;
    align-items: flex-end;
    gap: 10px;
    max-width: 100%;
}

/* User messages: right-aligned */
.msg-row.user {
    flex-direction: row-reverse;
}

/* Assistant messages: left-aligned */
.msg-row.assistant {
    flex-direction: row;
}

.msg-avatar {
    font-size: 28px;
    flex-shrink: 0;
    line-height: 1;
    padding-bottom: 4px;
}

.msg-bubble {
    max-width: 70%;
    padding: 12px 16px;
    border-radius: 18px;
    line-height: 1.6;
    font-size: 0.95rem;
    word-wrap: break-word;
}

/* User bubble: blue, right side */
.msg-bubble.user {
    background: #3B82F6;
    color: #FFFFFF;
    border-radius: 18px 18px 4px 18px;
}

/* Assistant bubble: yellow, left side */
.msg-bubble.assistant {
    background: #FEF3C7;
    color: #1F2937;
    border-radius: 18px 18px 18px 4px;
    border: 1px solid #FDE68A;
}

/* Escalation notice bubble */
.msg-bubble.escalation {
    background: #EFF6FF;
    color: #1D4ED8;
    border-radius: 18px;
    border: 1px solid #BFDBFE;
    font-style: italic;
}

</style>
""", unsafe_allow_html=True)



# ================= HELPERS =================

def _md_to_html(text: str) -> str:
    """Convert basic markdown to safe HTML for chat bubbles."""
    # Escape HTML special characters first
    text = html.escape(text)
    # Bold: **text**
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    # Italic: *text*
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
    # Newlines → <br>
    text = text.replace('\n', '<br>')
    return text


def render_message(role: str, content: str, bubble_type: str = "") -> None:
    """
    Render a chat message as a styled HTML bubble.

    Args:
        role: 'user' or 'assistant'
        content: Message text (supports basic markdown)
        bubble_type: Optional extra CSS class (e.g., 'escalation')
    """
    avatar = "👤" if role == "user" else "🤖"
    bubble_class = bubble_type if bubble_type else role
    html_content = _md_to_html(content)

    st.markdown(
        f"""
        <div class="msg-row {role}">
            <div class="msg-avatar">{avatar}</div>
            <div class="msg-bubble {bubble_class}">{html_content}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


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
    st.title("🤖 AELON")
    mode = st.selectbox("Mode", ["Utilisateur", "Admin"])

# ================= STORAGE =================
INTERACTIONS_FILE = Path(__file__).resolve().parent / "interactions.json"

def load_data():
    if INTERACTIONS_FILE.exists():
        with open(INTERACTIONS_FILE, encoding="utf-8") as f:
            return json.load(f)
    return []

def save_data(data):
    with open(INTERACTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# ================= ADMIN =================
if mode == "Admin":
    import pandas as pd
    import plotly.express as px

    st.title("📊 Dashboard Admin – AELON")

    data = load_data()

    if not data:
        st.warning("⚠️ Aucune donnée disponible. Lancez quelques conversations pour alimenter le dashboard.")
        st.stop()

    # ── Enrich data: add missing fields ──────────────────────────────────────
    for record in data:
        if "category" not in record or not record["category"]:
            record["category"] = detect_category(record.get("query", ""))
        if "escalated" not in record:
            record["escalated"] = record.get("agent", "L0") == "L1"
        if "resolution_status" not in record:
            record["resolution_status"] = "resolved" if not record.get("escalated") else "escalated"

    df = pd.DataFrame(data)

    # ── Sidebar Filters ───────────────────────────────────────────────────────
    st.sidebar.markdown("## 🔍 Filtres")

    all_categories = ["Toutes"] + sorted(df["category"].unique().tolist())
    selected_category = st.sidebar.selectbox("Catégorie", all_categories)

    all_agents = ["Tous"] + sorted(df["agent"].unique().tolist()) if "agent" in df.columns else ["Tous"]
    selected_agent = st.sidebar.selectbox("Agent", all_agents)

    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        min_date = df["timestamp"].min().date() if not df["timestamp"].isna().all() else None
        max_date = df["timestamp"].max().date() if not df["timestamp"].isna().all() else None
        if min_date and max_date and min_date != max_date:
            date_range = st.sidebar.date_input(
                "Période",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
            )
        else:
            date_range = None
    else:
        date_range = None

    # ── Apply filters ─────────────────────────────────────────────────────────
    df_filtered = df.copy()

    if selected_category != "Toutes":
        df_filtered = df_filtered[df_filtered["category"] == selected_category]

    if selected_agent != "Tous" and "agent" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["agent"] == selected_agent]

    if date_range and "timestamp" in df_filtered.columns and len(date_range) == 2:
        start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
        df_filtered = df_filtered[
            (df_filtered["timestamp"] >= start) & (df_filtered["timestamp"] <= end)
        ]

    # ── KPIs ─────────────────────────────────────────────────────────────────
    st.markdown("### 📈 Indicateurs clés")

    total = len(df_filtered)
    escalated_count = int(df_filtered["escalated"].sum()) if "escalated" in df_filtered.columns else 0
    escalation_rate = (escalated_count / total * 100) if total > 0 else 0
    avg_fraud = df_filtered["fraud_score"].mean() if "fraud_score" in df_filtered.columns else 0
    fraud_blocked = int((df_filtered["agent"] == "blocked").sum()) if "agent" in df_filtered.columns else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💬 Interactions", total)
    col2.metric("🔄 Escalades L1", escalated_count, f"{escalation_rate:.1f}%")
    col3.metric("🛡️ Score fraude moyen", f"{avg_fraud:.1f}")
    col4.metric("🚨 Requêtes bloquées", fraud_blocked)

    st.markdown("---")

    # ── Charts ────────────────────────────────────────────────────────────────
    CATEGORY_COLORS = {
        "connexion": "#3B82F6",
        "paiement": "#10B981",
        "carte": "#F59E0B",
        "fraude": "#EF4444",
        "autre": "#8B5CF6",
    }
    AGENT_COLORS = {"L0": "#3B82F6", "L1": "#10B981", "blocked": "#EF4444"}

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("#### 📂 Répartition par catégorie")
        if "category" in df_filtered.columns and not df_filtered.empty:
            cat_counts = df_filtered["category"].value_counts().reset_index()
            cat_counts.columns = ["Catégorie", "Nombre"]
            fig_cat = px.pie(
                cat_counts,
                values="Nombre",
                names="Catégorie",
                color="Catégorie",
                color_discrete_map=CATEGORY_COLORS,
                hole=0.4,
            )
            fig_cat.update_layout(
                margin=dict(t=10, b=10, l=10, r=10),
                legend=dict(orientation="h", yanchor="bottom", y=-0.3),
            )
            st.plotly_chart(fig_cat, use_container_width=True)

    with col_right:
        st.markdown("#### 🤖 Répartition L0 / L1")
        if "agent" in df_filtered.columns and not df_filtered.empty:
            agent_counts = df_filtered["agent"].value_counts().reset_index()
            agent_counts.columns = ["Agent", "Nombre"]
            fig_agent = px.bar(
                agent_counts,
                x="Agent",
                y="Nombre",
                color="Agent",
                color_discrete_map=AGENT_COLORS,
                text="Nombre",
            )
            fig_agent.update_layout(
                margin=dict(t=10, b=10, l=10, r=10),
                showlegend=False,
            )
            fig_agent.update_traces(textposition="outside")
            st.plotly_chart(fig_agent, use_container_width=True)

    col_left2, col_right2 = st.columns(2)

    with col_left2:
        st.markdown("#### 😊 Répartition des sentiments")
        if "sentiment" in df_filtered.columns and not df_filtered.empty:
            sent_counts = df_filtered["sentiment"].dropna().value_counts().reset_index()
            sent_counts.columns = ["Sentiment", "Nombre"]
            fig_sent = px.bar(
                sent_counts,
                x="Sentiment",
                y="Nombre",
                color="Sentiment",
                color_discrete_sequence=px.colors.qualitative.Pastel,
                text="Nombre",
            )
            fig_sent.update_layout(margin=dict(t=10, b=10, l=10, r=10), showlegend=False)
            fig_sent.update_traces(textposition="outside")
            st.plotly_chart(fig_sent, use_container_width=True)

    with col_right2:
        st.markdown("#### 🛡️ Distribution des scores de fraude")
        if "fraud_score" in df_filtered.columns and not df_filtered.empty:
            fig_fraud = px.histogram(
                df_filtered,
                x="fraud_score",
                nbins=10,
                color_discrete_sequence=["#EF4444"],
                labels={"fraud_score": "Score de fraude", "count": "Nombre"},
            )
            fig_fraud.update_layout(margin=dict(t=10, b=10, l=10, r=10))
            st.plotly_chart(fig_fraud, use_container_width=True)

    # ── Category bar chart ─────────────────────────────────────────────────
    st.markdown("#### 📊 Volume par catégorie")
    if "category" in df_filtered.columns and not df_filtered.empty:
        cat_bar = df_filtered["category"].value_counts().reset_index()
        cat_bar.columns = ["Catégorie", "Nombre"]
        fig_cat_bar = px.bar(
            cat_bar,
            x="Catégorie",
            y="Nombre",
            color="Catégorie",
            color_discrete_map=CATEGORY_COLORS,
            text="Nombre",
        )
        fig_cat_bar.update_layout(margin=dict(t=10, b=10, l=10, r=10), showlegend=False)
        fig_cat_bar.update_traces(textposition="outside")
        st.plotly_chart(fig_cat_bar, use_container_width=True)

    st.markdown("---")

    # ── Business Insights ────────────────────────────────────────────────────
    st.markdown("### 💡 Insights métier")

    if not df_filtered.empty:
        top_category = df_filtered["category"].value_counts().idxmax() if "category" in df_filtered.columns else "N/A"
        top_label = get_category_label(top_category)

        insight_col1, insight_col2 = st.columns(2)
        with insight_col1:
            st.info(f"**Problème le plus fréquent :** {top_label}")
            if escalation_rate > 30:
                st.warning(f"⚠️ Taux d'escalade élevé ({escalation_rate:.1f}%). Envisagez d'enrichir la base de connaissance L0.")
            else:
                st.success(f"✅ Taux d'escalade maîtrisé ({escalation_rate:.1f}%)")

        with insight_col2:
            if "category" in df_filtered.columns:
                fraud_cat = df_filtered[df_filtered["category"] == "fraude"]
                if len(fraud_cat) > 0:
                    st.error(f"🚨 {len(fraud_cat)} requête(s) liée(s) à de la fraude détectée(s).")
                escalated_df = df_filtered[df_filtered["escalated"]] if "escalated" in df_filtered.columns else pd.DataFrame()
                if not escalated_df.empty and "category" in escalated_df.columns:
                    top_escalated_cat = escalated_df["category"].value_counts().idxmax()
                    st.info(f"📌 Catégorie avec le plus d'escalades : **{get_category_label(top_escalated_cat)}**")

    st.markdown("---")

    # ── Data Table ───────────────────────────────────────────────────────────
    st.markdown("### 🗂️ Historique des interactions")

    display_cols = [c for c in ["timestamp", "query", "category", "agent", "escalated", "fraud_score", "risk_level", "sentiment", "resolution_status"] if c in df_filtered.columns]
    st.dataframe(
        df_filtered[display_cols].sort_values("timestamp", ascending=False) if "timestamp" in df_filtered.columns else df_filtered[display_cols],
        use_container_width=True,
        hide_index=True,
    )

    # ── CSV Export ───────────────────────────────────────────────────────────
    st.markdown("### 📥 Export des données")

    csv_data = interactions_to_csv(df_filtered.to_dict(orient="records"))
    st.download_button(
        label="⬇️ Télécharger CSV",
        data=csv_data,
        file_name=f"aelon_interactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        help="Télécharger les interactions filtrées au format CSV",
    )

# ================= USER =================
else:

    # ===== SESSION CHAT =====
    if "messages" not in st.session_state:
        st.session_state.messages = []

        # ✅ message de bienvenue
        st.session_state.messages.append({
            "role": "assistant",
            "content": "👋 Bonjour, je suis **AELON**, votre assistant bancaire.\n\nComment puis-je vous aider aujourd'hui ?",
        })

        # ✅ message sécurité
        st.session_state.messages.append({
            "role": "assistant",
            "content": "🔐 **Important :** Ne partagez jamais vos informations sensibles (mot de passe, code OTP, numéro de carte).",
        })

    # ===== HEADER =====
    col1, col2 = st.columns([1, 6])

    with col1:
        st.image("https://cdn-icons-png.flaticon.com/512/4712/4712100.png", width=60)

    with col2:
        st.markdown("## 💬 Assistant AELON")

    st.markdown("---")

    # ===== QUESTIONS RAPIDES =====
    st.markdown("### ⚡ Questions fréquentes")

    col1, col2, col3 = st.columns(3)

    if col1.button("🔐 Problème de connexion"):
        st.session_state.messages.append({"role": "user", "content": "je n'arrive pas à me connecter à mon compte"})

    if col2.button("💳 Carte refusée"):
        st.session_state.messages.append({"role": "user", "content": "ma carte est refusée"})

    if col3.button("💸 Virement échoué"):
        st.session_state.messages.append({"role": "user", "content": "mon virement ne passe pas"})

    st.markdown("---")

    # ===== CHAT HISTORY =====
    for msg in st.session_state.messages:
        bubble_type = msg.get("bubble_type", "")
        render_message(msg["role"], msg["content"], bubble_type)

    # ===== INPUT =====
    user_input = st.chat_input("Écrivez votre message...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        render_message("user", user_input)

    # ===== TRAITEMENT =====
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":

        user_query = st.session_state.messages[-1]["content"]

        # ===== FRAUD =====
        fraud_result = fraud_agent.analyze(user_query)

        if fraud_result["is_fraud"]:
            response = "🚨 Message suspect détecté. Veuillez contacter le support directement."
            agent_used = "blocked"
            escalated = False
            escalation_reason = None
            render_message("assistant", response)
            st.session_state.messages.append({"role": "assistant", "content": response})

        else:
            # ===== ORCHESTRATOR =====
            with st.spinner("🤔 AELON réfléchit..."):
                result = orchestrator.handle_user_query(user_query)

            if isinstance(result, dict):
                response = result.get("response", "")
                escalated = result.get("escalated", False)
                escalation_reason = result.get("escalation_reason")
                agent_used = result.get("agent", "L0")
            else:
                response = str(result)
                escalated = False
                escalation_reason = None
                agent_used = "L0"

            # ===== ESCALADE : message intermédiaire =====
            if escalated:
                transfer_msg = "🔄 Je transmets votre demande à un conseiller spécialisé. Veuillez patienter..."
                render_message("assistant", transfer_msg, bubble_type="escalation")
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": transfer_msg,
                    "bubble_type": "escalation",
                })

            # ===== AFFICHAGE RÉPONSE =====
            render_message("assistant", response)
            st.session_state.messages.append({"role": "assistant", "content": response})

        # ===== LOG DATA =====
        sentiment_result = {}
        try:
            sentiment_result = sentiment_agent.analyze(user_query)
        except Exception:
            pass

        record = {
            "timestamp": datetime.now().isoformat(),
            "query": user_query,
            "query_length": len(user_query),
            "category": detect_category(user_query),
            "fraud_score": fraud_result["score"],
            "risk_level": fraud_result["risk_level"],
            "is_fraud": fraud_result["is_fraud"],
            "fraud_reasons": fraud_result.get("reasons", []),
            "agent": agent_used,
            "escalated": escalated if not fraud_result["is_fraud"] else False,
            "escalation_reason": escalation_reason if not fraud_result["is_fraud"] else None,
            "response_preview": response[:100],
            "sentiment": sentiment_result.get("sentiment", ""),
            "resolution_status": "blocked" if fraud_result["is_fraud"] else ("escalated" if escalated else "resolved"),
        }

        data = load_data()
        data.append(record)
        save_data(data)