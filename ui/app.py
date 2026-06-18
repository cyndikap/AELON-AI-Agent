# -*- coding: utf-8 -*-

# ================= IMPORTS =================

import sys
import json
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

/* ===== CHAT ===== */
[data-testid="stChatInput"] textarea {
    background: #FFFFFF !important;
    color: #1F2937 !important;
}

/* ===== CHAT MESSAGES — User (right) ===== */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    flex-direction: row-reverse !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"])
    [data-testid="stChatMessageContent"] {
    background: linear-gradient(135deg, #EFF6FF, #DBEAFE) !important;
    border-radius: 18px 3px 18px 18px !important;
    border: 1px solid #BFDBFE !important;
    color: #1e3a5f !important;
    margin-left: auto;
}

/* ===== CHAT MESSAGES — Assistant (yellow) ===== */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"])
    [data-testid="stChatMessageContent"] {
    background: linear-gradient(135deg, #FFFBEB, #FEF3C7) !important;
    border-left: 4px solid #FCD34D !important;
    border-radius: 3px 18px 18px 18px !important;
    color: #1F2937 !important;
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
    st.title("🤖 AELON")
    mode = st.selectbox("Mode", ["Utilisateur", "Admin"])

# ================= STORAGE =================
INTERACTIONS_FILE = "interactions.json"

def load_data():
    if Path(INTERACTIONS_FILE).exists():
        return json.load(open(INTERACTIONS_FILE))
    return []

def save_data(data):
    json.dump(data, open(INTERACTIONS_FILE, "w"), indent=2)

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

    df["timestamp"] = pd.to_datetime(df.get("timestamp", pd.Series(dtype=str)), errors="coerce")

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
                .rename(columns={"index": "category", "category": "count",
                                 "count": "count"})
            )
            # pandas value_counts() returns Series; reset_index gives (category, count)
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
                st.markdown(f"- *{str(q)[:60]}* — **{cnt}x**")
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
            st.markdown(f"✅ Résolus : **{resolved}** ({resolved/total*100:.0f}%)")
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

        # ✅ message de bienvenue
        st.session_state.messages.append({
            "role": "assistant",
            "content": "👋 Bonjour, je suis **AELON**, votre assistant bancaire.\n\nComment puis-je vous aider aujourd’hui ?"
        })

        # ✅ message sécurité
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

    col1, col2 = st.columns([1,6])

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
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # ===== INPUT =====
    user_input = st.chat_input("Écrivez votre message...")

    if user_input:
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
                    "🔄 Je transmets votre demande à un conseiller spécialisé. "
                    "Merci de patienter quelques instants..."
                )
                with st.chat_message("assistant"):
                    st.markdown(escalation_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": escalation_msg
                })

        # ===== AFFICHAGE =====
        with st.chat_message("assistant"):
            st.markdown(response)

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