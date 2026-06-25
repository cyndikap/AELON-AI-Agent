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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root {
    --bg-main: #071629;
    --bg-side-top: #061224;
    --bg-side-bottom: #0B2447;
    --panel: #0C1C34;
    --border: #19395F;
    --text-main: #F8FAFC;
    --text-muted: #B8C7DE;
    --user-bg: #2563EB;
    --user-border: #1D4ED8;
    --assistant-bg: #FDE68A;
    --assistant-border: #F5C84B;
    --assistant-text: #111827;
    --input-bg: #102745;
    --send-yellow: #FACC15;
}

/* Global layout */
html, body, .stApp {
    background: var(--bg-main) !important;
    color: var(--text-main);
    font-family: 'Inter', sans-serif;
}

[data-testid="stAppViewContainer"] {
    background: transparent !important;
}

.block-container {
    padding-top: 1rem !important;
    padding-bottom: 4.2rem !important;
    max-width: 1080px !important;
}

h1, h2, h3 {
    letter-spacing: -0.01em;
    color: var(--text-main);
}

p {
    color: var(--text-muted);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, var(--bg-side-top) 0%, var(--bg-side-bottom) 100%);
    border-right: 1px solid var(--border);
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
    letter-spacing: 0.3px;
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
    background: rgba(255, 255, 255, 0.07);
    border: 1px solid rgba(147, 197, 253, 0.25);
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

/* Core controls */
input, textarea {
    background-color: #FFFFFF !important;
    color: var(--text-main) !important;
    border-radius: 10px !important;
    border: 1px solid #294A74 !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
}

input:focus, textarea:focus {
    border-color: #38BDF8 !important;
    box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.25) !important;
}

div[data-baseweb="select"] {
    background-color: #FFFFFF !important;
    border: 1px solid #294A74 !important;
    border-radius: 10px !important;
    min-height: 42px;
}

div[data-baseweb="select"] div,
div[data-baseweb="select"] span,
div[data-baseweb="select"] input {
    color: #0F172A !important;
}

/* Date input — match selectbox text color */
div[data-baseweb="input"] input,
div[data-baseweb="input"] span,
[data-testid="stDateInput"] input,
[data-testid="stDateInput"] span {
    color: #0F172A !important;
    background-color: #FFFFFF !important;
}

div[role="listbox"] {
    background-color: #FFFFFF !important;
}

div[role="option"] {
    color: #1F2937 !important;
}

div[role="option"]:hover {
    background-color: #EEF2FF !important;
}

button[kind="primary"],
[data-testid="baseButton-primary"] {
    background: linear-gradient(135deg, #FACC15, #FBBF24) !important;
    color: #111827 !important;
    font-weight: 700 !important;
    border-radius: 12px !important;
    border: 1px solid #F4B400 !important;
}

button {
    background: linear-gradient(135deg, #1D4ED8, #0EA5E9) !important;
    color: white !important;
    border-radius: 10px !important;
    border: none !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease !important;
}

button:hover {
    transform: translateY(-1px);
    box-shadow: 0 8px 16px rgba(14, 165, 233, 0.25);
}

/* Admin cards */
.card {
    background: var(--panel);
    border-radius: 14px;
    padding: 1rem;
    border: 1px solid var(--border);
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.22);
}

.decision-card {
    background: #0F2747;
    border: 1px solid #2C4F78;
    border-radius: 14px;
    padding: 12px 14px;
    color: #E2E8F0;
    box-shadow: 0 10px 20px rgba(2, 6, 23, 0.26);
    margin-bottom: 0.6rem;
}

.decision-card p,
.decision-card li,
.decision-card strong {
    color: #E2E8F0 !important;
}

.admin-hero {
    background:
        linear-gradient(120deg, rgba(37, 99, 235, 0.16) 0%, rgba(14, 165, 233, 0.12) 55%, rgba(250, 204, 21, 0.12) 100%),
        rgba(13, 34, 61, 0.85);
    border: 1px solid #2A4D78;
    border-radius: 16px;
    padding: 14px 16px;
    box-shadow: 0 14px 26px rgba(2, 6, 23, 0.35);
    margin-bottom: 10px;
}

.admin-hero h4 {
    margin: 0;
    color: #F8FAFC;
    font-size: 1.02rem;
}

.admin-hero p {
    margin: 6px 0 0 0;
    color: #B8C7DE;
    font-size: 0.92rem;
}

[data-testid="stMetric"] {
    background: linear-gradient(180deg, #0F2747 0%, #112D50 100%);
    padding: 15px;
    border-radius: 12px;
    border: 1px solid #2A4D78;
    box-shadow: 0 12px 22px rgba(2, 6, 23, 0.28);
    border-top: 4px solid #FACC15;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

[data-testid="stMetric"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 16px 28px rgba(2, 6, 23, 0.36);
}

[data-testid="stMetricValue"] {
    color: #F8FAFC !important;
}

[data-testid="stMetricLabel"] {
    color: #C7D6EA !important;
}

.vega-embed text {
    fill: #E2E8F0 !important;
}

/* Chat input zone */
[data-testid="stChatInput"] textarea {
    background: var(--input-bg) !important;
    color: #F8FAFC !important;
    border: 1px solid #2A4D78 !important;
    box-shadow: 0 6px 14px rgba(2, 6, 23, 0.34) !important;
    min-height: 52px !important;
    border-radius: 14px !important;
}

[data-testid="stChatInput"] textarea:focus {
    border-color: #38BDF8 !important;
    box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.2) !important;
}

[data-testid="stChatInput"] button {
    background: linear-gradient(135deg, #FACC15, #FBBF24) !important;
    color: #111827 !important;
    border: 1px solid #EAB308 !important;
    border-radius: 12px !important;
}

[data-testid="chatAvatarIcon-assistant"] {
    background: linear-gradient(135deg, #FACC15, #FBBF24) !important;
    border-radius: 10px !important;
    padding: 8px !important;
    box-shadow: 0 0 12px rgba(250, 204, 21, 0.52) !important;
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
    color: #F8FAFC;
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
    width: 2.2rem !important;
    height: 2.2rem !important;
    min-width: 2.2rem !important;
    min-height: 2.2rem !important;
    flex: 0 0 2.2rem !important;
}

[data-testid="stChatMessage"] [data-testid="stChatMessageAvatar"] img,
[data-testid="stChatMessage"] [data-testid="stChatMessageAvatar"] svg,
[data-testid="stChatMessage"] [data-testid="stChatMessageAvatarUser"] img,
[data-testid="stChatMessage"] [data-testid="stChatMessageAvatarUser"] svg,
[data-testid="stChatMessage"] [data-testid="stChatMessageAvatarAssistant"] img,
[data-testid="stChatMessage"] [data-testid="stChatMessageAvatarAssistant"] svg {
    width: 100% !important;
    height: 100% !important;
    border-radius: 12px !important;
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
    background: var(--user-bg);
    border: 1px solid var(--user-border);
    color: #FFFFFF;
    border-radius: 18px 4px 18px 18px;
    animation: fadeSlideInRight 0.34s ease both;
}

.aelon-bubble-user::after {
    content: "";
    position: absolute;
    right: -9px;
    bottom: 10px;
    width: 0;
    height: 0;
    border-left: 10px solid var(--user-bg);
    border-top: 8px solid transparent;
    border-bottom: 8px solid transparent;
}

.aelon-bubble-assistant {
    background: var(--assistant-bg);
    border: 1px solid var(--assistant-border);
    color: var(--assistant-text);
    border-radius: 4px 18px 18px 18px;
    box-shadow: 0 0 0 1px rgba(245, 200, 75, 0.2), 0 0 16px rgba(245, 200, 75, 0.24), 0 8px 20px rgba(245, 200, 75, 0.28);
    animation: fadeSlideInLeft 0.34s ease both;
}

.aelon-bubble-assistant::before {
    content: "";
    position: absolute;
    left: -9px;
    bottom: 10px;
    width: 0;
    height: 0;
    border-right: 10px solid var(--assistant-bg);
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
    gap: 0rem !important;
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
    background: var(--user-bg) !important;
    border: 1px solid var(--user-border) !important;
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
    border-left: 10px solid var(--user-bg);
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
    background: var(--assistant-bg) !important;
    border: 1px solid var(--assistant-border) !important;
    border-radius: 3px 18px 18px 18px !important;
    color: var(--assistant-text) !important;
    display: inline-block;
    width: fit-content;
    max-width: min(78%, 760px);
    box-shadow: 0 0 0 1px rgba(245, 200, 75, 0.18), 0 0 16px rgba(245, 200, 75, 0.26), 0 8px 20px rgba(245, 200, 75, 0.28);
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
    border-right: 10px solid var(--assistant-bg);
    border-top: 8px solid transparent;
    border-bottom: 8px solid transparent;
}

/* ===== SIDEBAR NAV ITEMS ===== */
[data-testid="stSidebar"] [role="radiogroup"] {
    gap: 0;
    display: flex;
    flex-direction: column;
    width: 100%;
}

/* Inactive card — mirrors .sidebar-info exactly */
[data-testid="stSidebar"] [role="radio"] {
    background: rgba(255, 255, 255, 0.07);
    border: 1px solid rgba(147, 197, 253, 0.25);
    border-radius: 10px;
    padding: 10px 12px;
    margin-bottom: 6px;
    cursor: pointer;
    display: flex;
    align-items: center;
    width: 100%;
    transition: background 0.18s ease, border-color 0.18s ease, box-shadow 0.18s ease;
}

/* Hover */
[data-testid="stSidebar"] [role="radio"]:hover {
    background: rgba(255, 255, 255, 0.11);
    border-color: rgba(147, 197, 253, 0.5);
}

/* Active card — yellow accent */
[data-testid="stSidebar"] [role="radio"][aria-checked="true"] {
    background: rgba(250, 204, 21, 0.10);
    border-color: rgba(250, 204, 21, 0.45);
    border-left: 3px solid #FACC15;
    box-shadow: 0 4px 14px rgba(250, 204, 21, 0.10);
}

/* Hide native radio circle dot */
[data-testid="stSidebar"] [role="radio"] svg {
    display: none !important;
}

/* Remove gap left by hidden svg container */
[data-testid="stSidebar"] [role="radio"] > div:first-child {
    display: none !important;
}

/* Nav label text — inactive */
[data-testid="stSidebar"] [role="radio"] p,
[data-testid="stSidebar"] [role="radio"] label,
[data-testid="stSidebar"] [role="radio"] span {
    font-size: 0.92rem !important;
    font-weight: 500 !important;
    color: #B8C7DE !important;
    letter-spacing: 0.01em;
    transition: color 0.15s ease;
}

/* Nav label text — active */
[data-testid="stSidebar"] [role="radio"][aria-checked="true"] p,
[data-testid="stSidebar"] [role="radio"][aria-checked="true"] label,
[data-testid="stSidebar"] [role="radio"][aria-checked="true"] span {
    color: #FACC15 !important;
    font-weight: 600 !important;
}

[data-testid="stDataFrame"] {
    border: 1px solid var(--border);
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 12px 22px rgba(2, 6, 23, 0.28);
}

[data-testid="stAlert"] {
    border-radius: 12px !important;
    border: 1px solid var(--border) !important;
}

@media (max-width: 900px) {
    .block-container {
        padding-top: 0.8rem !important;
        padding-left: 0.85rem !important;
        padding-right: 0.85rem !important;
    }

    .chat-header-avatar {
        width: 64px;
        height: 64px;
    }

    .chat-header-title {
        font-size: 1.1rem;
    }
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


with st.sidebar:

    st.markdown("###  Navigation")

    page = st.selectbox(
        "",
        ["💬 Chat Assistant", " Dashboard Admin"]
    )

    mode = "Utilisateur" if page == "💬 Chat Assistant" else "Admin"

    if mode == "Admin":
        st.markdown('<hr class="sidebar-sep" />', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-section">Dashboard</div>', unsafe_allow_html=True)
        page = st.radio(
            "Page dashboard",
            [
                "📊 Vue globale",
                "📈 Analyse des sentiments",
                "🔁 Analyse des escalades (L0 / L1)",
                "🚨 Analyse des fraudes",
                "📂 Analyse des requêtes / catégories",
            ],
            label_visibility="collapsed",
        )
    else:
        page = None

    st.markdown('<hr class="sidebar-sep" />', unsafe_allow_html=True)
    if mode == "Utilisateur":
        st.markdown('<div class="sidebar-section">Informations</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="sidebar-info">Mode actif : <b>{mode}</b></div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-info">Ne partagez jamais vos identifiants</div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-info">Paiements et fraude : priorité élevée</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="sidebar-info">Dernière mise à jour : {datetime.now().strftime("%H:%M")}</div>', unsafe_allow_html=True)
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

    st.title("📊 Dashboard Administrateur — AELON")
    st.markdown(
        """
        <div class="admin-hero">
            <h4>Centre de Décision Métier</h4>
            <p>Analysez les tendances, comprenez les causes et appliquez des recommandations concrètes.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    data = load_data()
    if not data:
        st.warning("⚠️ Pas de données disponibles. Lancez quelques conversations en mode Utilisateur d'abord.")
        st.stop()

    df = pd.DataFrame(data)

    if "query" not in df.columns:
        df["query"] = ""

    if "category" not in df.columns:
        df["category"] = df["query"].apply(detect_category)
    else:
        df["category"] = df["category"].fillna("autre")

    if "agent" not in df.columns:
        df["agent"] = "L0"
    df["agent"] = df["agent"].fillna("L0")

    if "escalated" not in df.columns:
        df["escalated"] = df["agent"].eq("L1")
    df["escalated"] = df["escalated"].fillna(False).astype(bool)

    if "sentiment" not in df.columns:
        df["sentiment"] = "neutral"
    df["sentiment"] = df["sentiment"].fillna("neutral")

    if "fraud_score" not in df.columns:
        df["fraud_score"] = 0
    df["fraud_score"] = pd.to_numeric(df["fraud_score"], errors="coerce").fillna(0)

    if "risk_level" not in df.columns:
        df["risk_level"] = "LOW"

    if "is_fraud" not in df.columns:
        df["is_fraud"] = df["agent"].eq("blocked")

    df["timestamp"] = pd.to_datetime(
        df["timestamp"] if "timestamp" in df.columns else pd.Series(dtype=str),
        errors="coerce",
    )

    # Filters
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔍 Filtres Dashboard")

    categories_opts = ["Toutes"] + sorted(df["category"].dropna().unique().tolist())
    sel_category = st.sidebar.selectbox("Catégorie", categories_opts)

    agents_opts = ["Tous"] + sorted(df["agent"].dropna().unique().tolist())
    sel_agent = st.sidebar.selectbox("Agent", agents_opts)

    valid_dates = df["timestamp"].dropna()
    if len(valid_dates) > 0:
        min_date = valid_dates.min().date()
        max_date = valid_dates.max().date()
        date_range = st.sidebar.date_input(
            "Période", value=(min_date, max_date), min_value=min_date, max_value=max_date
        )
    else:
        date_range = None

    filtered = df.copy()
    if sel_category != "Toutes":
        filtered = filtered[filtered["category"] == sel_category]
    if sel_agent != "Tous":
        filtered = filtered[filtered["agent"] == sel_agent]
    if date_range and len(date_range) == 2:
        filtered = filtered[
            (filtered["timestamp"].dt.date >= date_range[0])
            & (filtered["timestamp"].dt.date <= date_range[1])
        ]

    total = len(filtered)
    if total == 0:
        st.info("Aucune interaction pour les filtres sélectionnés.")
        st.stop()

    def render_decision_cards(analysis_text: str, recommendations: list[str]) -> None:
        st.markdown("### 🔎 Analyse")
        st.markdown(
            f'<div class="decision-card"><p>{analysis_text}</p></div>',
            unsafe_allow_html=True,
        )
        rec_html = "".join([f"<li>{r}</li>" for r in recommendations])
        st.markdown("### 💡 Recommandations")
        st.markdown(
            f'<div class="decision-card"><ul>{rec_html}</ul></div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")

    if page == "📊 Vue globale":
        st.subheader("📊 Vue globale")

        n_escalated = int(filtered["escalated"].sum())
        escalation_rate = (n_escalated / total * 100) if total else 0
        avg_fraud = float(filtered["fraud_score"].mean()) if total else 0
        neg_rate = float(filtered["sentiment"].isin(["frustrated", "angry", "negative"]).mean() * 100)
        top_cat = filtered["category"].mode()[0] if total else "N/A"

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Interactions", total)
        k2.metric("Taux d'escalade", f"{escalation_rate:.1f}%")
        k3.metric("Score fraude moyen", f"{avg_fraud:.1f}")
        k4.metric("Catégorie principale", f"{CATEGORY_ICONS.get(top_cat, '❓')} {str(top_cat).capitalize()}")

        timeline = filtered.copy()
        timeline["day"] = timeline["timestamp"].dt.floor("D")
        vol = timeline.groupby(["day", "agent"]).size().reset_index(name="count")
        main_chart = (
            alt.Chart(vol)
            .mark_area(opacity=0.7)
            .encode(
                x=alt.X("day:T", title="Date"),
                y=alt.Y("count:Q", title="Volume"),
                color=alt.Color(
                    "agent:N",
                    scale=alt.Scale(domain=["L0", "L1", "blocked"], range=["#2563EB", "#14B8A6", "#EF4444"]),
                    legend=alt.Legend(title="Agent"),
                ),
                tooltip=["day:T", "agent:N", "count:Q"],
            )
            .properties(height=320)
        )
        st.altair_chart(main_chart, use_container_width=True)

        if escalation_rate > 35 or neg_rate > 40:
            analysis = "Le tableau global montre une pression opérationnelle élevée. Les signaux combinés (escalades + sentiments négatifs) indiquent un risque de dégradation de l'expérience client."
        elif avg_fraud > 35:
            analysis = "La dynamique globale est marquée par une hausse du risque fraude. La surveillance opérationnelle doit être renforcée à court terme."
        else:
            analysis = "La performance globale est stable. Les indicateurs restent maîtrisés et permettent une amélioration continue par optimisation ciblée."

        recs = [
            "Prioriser les catégories les plus fréquentes dans le plan d'amélioration.",
            "Renforcer les réponses L0 sur les motifs d'escalade les plus courants.",
            "Suivre hebdomadairement les KPI risque/satisfaction pour ajuster les actions.",
        ]
        render_decision_cards(analysis, recs)

    elif page == "📈 Analyse des sentiments":
        st.subheader("📈 Analyse des sentiments")

        sent_counts = filtered["sentiment"].value_counts().reset_index()
        sent_counts.columns = ["sentiment", "count"]
        sentiment_chart = (
            alt.Chart(sent_counts)
            .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
            .encode(
                x=alt.X("sentiment:N", title="Sentiment"),
                y=alt.Y("count:Q", title="Nombre d'interactions"),
                color=alt.Color("sentiment:N", scale=alt.Scale(scheme="tableau10"), legend=None),
                tooltip=["sentiment:N", "count:Q"],
            )
            .properties(height=320)
        )
        st.altair_chart(sentiment_chart, use_container_width=True)

        neg_rate = float(filtered["sentiment"].isin(["frustrated", "angry", "negative"]).mean() * 100)
        if neg_rate >= 35:
            analysis = "Un nombre important d’interactions est associé à un sentiment négatif, ce qui peut indiquer des problèmes dans l’expérience client."
        elif neg_rate >= 20:
            analysis = "Le sentiment client devient sensible sur une part notable des échanges. Une action préventive est recommandée pour éviter une dégradation."
        else:
            analysis = "La perception client reste globalement positive ou neutre, ce qui suggère une expérience relativement fluide."

        recs = [
            "Améliorer les réponses du chatbot sur les cas d'incompréhension fréquents.",
            "Simplifier les parcours utilisateurs sur les demandes récurrentes.",
            "Créer des réponses courtes et rassurantes pour les situations à forte frustration.",
        ]
        render_decision_cards(analysis, recs)

    elif page == "🔁 Analyse des escalades (L0 / L1)":
        st.subheader("🔁 Analyse des escalades (L0 / L1)")

        agent_counts = filtered["agent"].value_counts().reset_index()
        agent_counts.columns = ["agent", "count"]
        escalation_chart = (
            alt.Chart(agent_counts)
            .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
            .encode(
                x=alt.X("agent:N", title="Niveau de traitement"),
                y=alt.Y("count:Q", title="Nombre de cas"),
                color=alt.Color(
                    "agent:N",
                    scale=alt.Scale(domain=["L0", "L1", "blocked"], range=["#2563EB", "#14B8A6", "#EF4444"]),
                    legend=None,
                ),
                tooltip=["agent:N", "count:Q"],
            )
            .properties(height=320)
        )
        st.altair_chart(escalation_chart, use_container_width=True)

        l1_rate = float((filtered["agent"] == "L1").mean() * 100)
        if l1_rate >= 30:
            analysis = "Le taux d’escalade est élevé, ce qui suggère que les requêtes ne sont pas suffisamment traitées au niveau L0."
        elif l1_rate >= 18:
            analysis = "Le volume d'escalade reste significatif. Certains motifs pourraient être absorbés par une meilleure couverture L0."
        else:
            analysis = "Le routage est globalement efficace, avec une majorité de cas résolus au niveau L0."

        recs = [
            "Améliorer le routage L0 sur les catégories les plus escaladées.",
            "Enrichir la base de connaissances avec les cas transférés vers L1.",
            "Mettre en place une revue hebdomadaire des raisons d'escalade.",
        ]
        render_decision_cards(analysis, recs)

    elif page == "🚨 Analyse des fraudes":
        st.subheader("🚨 Analyse des fraudes")

        fraud_counts = filtered.groupby("risk_level").size().reset_index(name="count")
        fraud_chart = (
            alt.Chart(fraud_counts)
            .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
            .encode(
                x=alt.X("risk_level:N", title="Niveau de risque"),
                y=alt.Y("count:Q", title="Nombre de cas"),
                color=alt.Color(
                    "risk_level:N",
                    scale=alt.Scale(domain=["LOW", "MEDIUM", "HIGH", "low", "medium", "high"],
                                    range=["#22C55E", "#F59E0B", "#EF4444", "#22C55E", "#F59E0B", "#EF4444"]),
                    legend=None,
                ),
                tooltip=["risk_level:N", "count:Q"],
            )
            .properties(height=320)
        )
        st.altair_chart(fraud_chart, use_container_width=True)

        fraud_rate = float(filtered["is_fraud"].fillna(False).mean() * 100)
        if fraud_rate >= 12 or float(filtered["fraud_score"].mean()) >= 40:
            analysis = "Une augmentation des cas potentiellement frauduleux a été détectée, nécessitant une surveillance renforcée."
        elif fraud_rate >= 5:
            analysis = "Des signaux de risque fraude sont présents à un niveau modéré. Une vigilance accrue est recommandée."
        else:
            analysis = "Le niveau de risque fraude reste contenu sur la période sélectionnée."

        recs = [
            "Renforcer les contrôles sur les scénarios de risque les plus fréquents.",
            "Améliorer les alertes temps réel et les seuils de déclenchement.",
            "Analyser les motifs textuels des cas suspects pour affiner les règles.",
        ]
        render_decision_cards(analysis, recs)

    else:
        st.subheader("📂 Analyse des requêtes / catégories")

        cat_counts = filtered["category"].value_counts().reset_index()
        cat_counts.columns = ["category", "count"]
        category_chart = (
            alt.Chart(cat_counts)
            .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
            .encode(
                x=alt.X("count:Q", title="Volume"),
                y=alt.Y("category:N", sort="-x", title="Catégorie"),
                color=alt.Color(
                    "category:N",
                    scale=alt.Scale(
                        domain=list(CATEGORY_COLORS.keys()),
                        range=list(CATEGORY_COLORS.values()),
                    ),
                    legend=None,
                ),
                tooltip=["category:N", "count:Q"],
            )
            .properties(height=340)
        )
        st.altair_chart(category_chart, use_container_width=True)

        top_queries = filtered["query"].value_counts().head(5).reset_index()
        top_queries.columns = ["requête", "fréquence"]
        st.dataframe(top_queries, use_container_width=True, hide_index=True)

        top_ratio = float(cat_counts.iloc[0]["count"] / total * 100) if total else 0
        if top_ratio >= 35:
            analysis = "Une catégorie domine nettement le volume de requêtes. Cela indique un besoin métier prioritaire sur ce segment."
        elif top_ratio >= 20:
            analysis = "La répartition des demandes montre quelques pôles majeurs, offrant des opportunités ciblées d'automatisation."
        else:
            analysis = "Les requêtes sont diversifiées, ce qui invite à une stratégie d'amélioration équilibrée par thématique."

        recs = [
            "Automatiser les cas récurrents à forte fréquence.",
            "Créer une FAQ orientée sur les 5 requêtes les plus posées.",
            "Mesurer l'impact des actions via un suivi hebdomadaire des volumes par catégorie.",
        ]
        render_decision_cards(analysis, recs)

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
    st.markdown(
        """
        <div class="chat-header">
            <img class="chat-header-avatar" src="https://cdn-icons-png.flaticon.com/512/4712/4712100.png" alt="AELON - Banking Assistant" />
            <div class="chat-header-title">Assistant AELON</div>
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
    st.markdown(
        '<div style="position:fixed;bottom:6px;left:0;right:0;text-align:center;'
        'font-size:0.68rem;color:#9CA3AF;pointer-events:none;z-index:9999;">'
        'En continuant cette conversation, vous acceptez que vos informations soient collectées '
        'et traitées conformément à notre politique de confidentialité.'
        '</div>',
        unsafe_allow_html=True,
    )

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