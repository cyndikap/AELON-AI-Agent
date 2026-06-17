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

    st.title("📊 Dashboard Admin")

    data = load_data()

    if not data:
        st.warning("Pas de données encore")

    df = pd.DataFrame(data)

    if "fraud_score" in df:
        st.subheader("Fraud Score Distribution")
        st.bar_chart(df["fraud_score"])

    if "agent" in df:
        st.subheader("Répartition L0 vs L1")
        st.bar_chart(df["agent"].value_counts())

    if "sentiment" in df:
        st.subheader("Sentiment")
        st.bar_chart(df["sentiment"].value_counts())

    if "risk_level" in df:
        st.subheader("Risque")
        st.bar_chart(df["risk_level"].value_counts())

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

        else:
            # ===== ORCHESTRATOR (tu ne touches PAS) =====
            response = orchestrator.handle_user_query(user_query)

            # déterminer agent (pour log)
            l0_result = l0_agent.handle(user_query)
            agent_used = "L0" if l0_result["decision"] == "answer" else "L1"

        # ===== AFFICHAGE =====
        with st.chat_message("assistant"):
            with st.spinner("AELON réfléchit..."):
                st.markdown(response)

        st.session_state.messages.append({
            "role": "assistant",
            "content": response
        })

        # ===== LOG DATA (backend inchangé) =====
        record = {
            "timestamp": datetime.now().isoformat(),
            "query": user_query,
            "query_length": len(user_query),
            "fraud_score": fraud_result["score"],
            "risk_level": fraud_result["risk_level"],
            "is_fraud": fraud_result["is_fraud"],
            "fraud_reasons": fraud_result.get("reasons", ""),
            "agent": agent_used,
            "response_preview": response[:100]
        }

        data = load_data()
        data.append(record)
        save_data(data)