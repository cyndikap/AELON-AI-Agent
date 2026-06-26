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

# ================= AVATAR =================
AELON_AVATAR = Path(__file__).resolve().parent / "aelon_avatar.png"
AELON_AVATAR_BYTES = AELON_AVATAR.read_bytes()

# ================= CONFIG =================
st.set_page_config(page_title="AELON", page_icon="⚡", layout="wide")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

:root {
    --bg-deep: #071629;
    --bg-page: #0A1D3A;
    --bg-card: #0F2747;
    --bg-surface: #112D50;
    --border: #1E446E;
    --border-bold: 3px solid #1E446E;
    --border-heavy: 4px solid #1E446E;
    --shadow: 0 8px 0 0 #0A1D3A;
    --shadow-sm: 0 4px 0 0 #0A1D3A;
    --shadow-lg: 0 10px 0 0 #0A1D3A;
    --yellow: #FACC15;
    --yellow-bg: #FDE68A;
    --yellow-border: #F5C84B;
    --gold: #FBBF24;
    --blue: #2563EB;
    --blue-dark: #1D4ED8;
    --teal: #14B8A6;
    --pink: #F87171;
    --text-main: #F1F5F9;
    --text-muted: #94A3B8;
    --text-dim: #64748B;
    /* === SaaS Accent (purple / pink) === */
    --purple: #7C3AED;
    --purple-dark: #6D28D9;
    --purple-light: #8B5CF6;
    --pink: #EC4899;
    --gradient-accent: linear-gradient(135deg, #7C3AED 0%, #EC4899 100%);
    --gradient-accent-soft: linear-gradient(135deg, rgba(124,58,237,0.15) 0%, rgba(236,72,153,0.10) 100%);
}

html, body, .stApp {
    background: var(--bg-deep) !important;
    font-family: 'Inter', sans-serif;
    color: var(--text-main);
}

[data-testid="stAppViewContainer"] {
    background: var(--bg-deep) !important;
}

.block-container {
    padding-top: 0.8rem !important;
    padding-bottom: 5rem !important;
    max-width: 1100px !important;
}

h1, h2, h3 {
    font-weight: 700;
    color: var(--text-main);
    letter-spacing: -0.02em;
}

h4, h5, h6 {
    font-weight: 600;
    color: var(--text-main);
}

p, li, span, div {
    color: var(--text-main);
}

/* ===== SIDEBAR ===== */
section[data-testid="stSidebar"] {
    background: var(--bg-card) !important;
    border-right: 3px solid var(--border);
    box-shadow: 6px 0 20px rgba(0, 0, 0, 0.3) !important;
    margin: 0;
    border-radius: 0 !important;
}

section[data-testid="stSidebar"] > div {
    padding: 0 !important;
}

section[data-testid="stSidebar"] * {
    color: var(--text-main) !important;
}

.sidebar-brand {
    text-align: center;
    padding: 28px 16px 18px 16px;
    border-bottom: 2px solid var(--border);
    margin-bottom: 12px;
    background: linear-gradient(180deg, rgba(37, 99, 235, 0.12) 0%, transparent 100%);
}

.sidebar-avatar {
    width: 72px;
    height: 72px;
    border-radius: 16px;
    object-fit: cover;
    border: 3px solid var(--border);
    background: linear-gradient(135deg, var(--blue) 0%, #1E40AF 100%);
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 2.2rem;
    box-shadow: 0 6px 16px rgba(37, 99, 235, 0.3);
}

.sidebar-title {
    margin-top: 14px;
    font-size: 1.5rem;
    font-weight: 800;
    color: var(--text-main);
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

.sidebar-subtitle {
    margin-top: 2px;
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--text-dim) !important;
    text-transform: uppercase;
    letter-spacing: 0.12em;
}

.sidebar-nav-label {
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    padding: 12px 16px 6px 16px;
    color: var(--text-dim) !important;
}

.sidebar-sep {
    border: 0;
    border-top: 1px solid var(--border);
    margin: 12px 16px;
    opacity: 0.6;
}

.sidebar-info {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 12px 14px;
    margin: 0 12px 10px 12px;
    font-size: 0.8rem;
    font-weight: 500;
    backdrop-filter: blur(4px);
}

.sidebar-info b {
    color: var(--yellow) !important;
}

.sidebar-footer {
    text-align: center;
    font-size: 0.72rem;
    font-weight: 500;
    color: var(--text-dim) !important;
    padding: 14px 16px;
    border-top: 1px solid var(--border);
    margin-top: 8px;
}

/* ===== SIDEBAR NAV RADIO ===== */
[data-testid="stSidebar"] [role="radiogroup"] {
    gap: 0;
    display: flex;
    flex-direction: column;
    padding: 0 12px;
}

[data-testid="stSidebar"] [role="radio"] {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid transparent;
    border-radius: 10px;
    padding: 11px 14px;
    margin-bottom: 6px;
    cursor: pointer;
    display: flex;
    align-items: center;
    width: 100%;
    transition: all 0.18s ease;
}

[data-testid="stSidebar"] [role="radio"]:hover {
    background: rgba(255, 255, 255, 0.07);
    border-color: var(--border);
}

[data-testid="stSidebar"] [role="radio"][aria-checked="true"] {
    background: var(--gradient-accent-soft);
    border-color: var(--purple-light);
    border-left: 3px solid var(--purple-light);
    box-shadow: 0 0 20px rgba(124, 58, 237, 0.12);
}

[data-testid="stSidebar"] [role="radio"] svg {
    display: none !important;
}

[data-testid="stSidebar"] [role="radio"] > div:first-child {
    display: none !important;
}

[data-testid="stSidebar"] [role="radio"] p,
[data-testid="stSidebar"] [role="radio"] label,
[data-testid="stSidebar"] [role="radio"] span {
    font-size: 0.88rem !important;
    font-weight: 600 !important;
    color: var(--text-muted) !important;
}

[data-testid="stSidebar"] [role="radio"][aria-checked="true"] p,
[data-testid="stSidebar"] [role="radio"][aria-checked="true"] label,
[data-testid="stSidebar"] [role="radio"][aria-checked="true"] span {
    color: var(--purple-light) !important;
    font-weight: 700 !important;
}

/* ===== SELECT BOX ===== */
div[data-baseweb="select"] {
    background: var(--bg-surface) !important;
    border: 2px solid var(--border) !important;
    border-radius: 10px !important;
    min-height: 42px;
    transition: border-color 0.2s ease;
}

div[data-baseweb="select"]:focus-within {
    border-color: var(--yellow) !important;
}

div[data-baseweb="select"] div,
div[data-baseweb="select"] span,
div[data-baseweb="select"] input {
    color: var(--text-main) !important;
    font-weight: 500 !important;
}

div[role="listbox"] {
    background: var(--bg-card) !important;
    border: 2px solid var(--border) !important;
    border-radius: 10px !important;
}

div[role="option"] {
    color: var(--text-main) !important;
    font-weight: 500 !important;
    padding: 10px 14px !important;
}

div[role="option"]:hover {
    background: rgba(37, 99, 235, 0.2) !important;
}

/* ===== DATE INPUT ===== */
div[data-baseweb="input"] input,
div[data-baseweb="input"] span,
[data-testid="stDateInput"] input,
[data-testid="stDateInput"] span {
    color: var(--text-main) !important;
    background: var(--bg-surface) !important;
    font-weight: 500 !important;
}

[data-testid="stDateInput"] > div {
    border: 2px solid var(--border) !important;
    border-radius: 10px !important;
    background: var(--bg-surface) !important;
}

/* ===== BUTTONS ===== */
button {
    border: 2px solid var(--border) !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    transition: all 0.18s ease !important;
    padding: 10px 20px !important;
}

button:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(37, 99, 235, 0.2) !important;
}

button[kind="primary"],
[data-testid="baseButton-primary"] {
    background: linear-gradient(135deg, var(--yellow) 0%, var(--gold) 100%) !important;
    color: #0F172A !important;
    border: 2px solid var(--yellow-border) !important;
    font-weight: 700 !important;
}

button:not([kind="primary"]) {
    background: linear-gradient(135deg, var(--blue) 0%, #1E40AF 100%) !important;
    color: white !important;
    border: 2px solid var(--blue-dark) !important;
}

button[kind="secondary"] {
    background: linear-gradient(135deg, var(--teal) 0%, #0D9488 100%) !important;
    border: 2px solid #0D9488 !important;
}

/* ===== ADMIN CARDS ===== */
.card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.2rem;
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.2);
}

.decision-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 14px 16px;
    color: var(--text-main);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
    margin-bottom: 0.8rem;
}

.decision-card p,
.decision-card li,
.decision-card strong {
    color: var(--text-main) !important;
}

.admin-hero {
    background: linear-gradient(135deg, rgba(37, 99, 235, 0.12) 0%, rgba(250, 204, 21, 0.08) 100%);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 18px 20px;
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.2);
    margin-bottom: 14px;
}

.admin-hero h4 {
    margin: 0;
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--yellow);
}

.admin-hero p {
    margin: 8px 0 0 0;
    font-weight: 400;
    color: var(--text-muted);
}

/* ===== METRICS ===== */
[data-testid="stMetric"] {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 16px;
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
    transition: all 0.2s ease;
    border-top: 3px solid var(--yellow);
}

[data-testid="stMetric"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.25);
    border-color: var(--yellow);
}

[data-testid="stMetricLabel"] {
    font-weight: 600 !important;
    color: var(--text-dim) !important;
    text-transform: uppercase !important;
    font-size: 0.68rem !important;
    letter-spacing: 0.06em !important;
}

[data-testid="stMetricValue"] {
    font-weight: 700 !important;
    color: var(--text-main) !important;
    font-size: 1.8rem !important;
}

/* ===== DATA FRAME ===== */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border);
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
}

[data-testid="stDataFrame"] th {
    background: var(--bg-surface) !important;
    color: var(--yellow) !important;
    font-weight: 600 !important;
    border-bottom: 2px solid var(--border) !important;
}

[data-testid="stDataFrame"] td {
    background: var(--bg-card) !important;
    color: var(--text-main) !important;
    font-weight: 400 !important;
}

/* ===== ALERTS ===== */
[data-testid="stAlert"] {
    border-radius: 10px !important;
    border: 1px solid var(--border) !important;
}

[data-testid="stAlert"] > div {
    background: var(--bg-card) !important;
    color: var(--text-main) !important;
    font-weight: 500 !important;
}

/* ===== CHAT HEADER ===== */
.chat-header {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 8px;
    margin-top: 4px;
    margin-bottom: 18px;
}

.chat-header-avatar {
    width: 76px;
    height: 76px;
    border-radius: 18px;
    border: 2px solid var(--border);
    background: linear-gradient(135deg, var(--blue) 0%, #1E40AF 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2.2rem;
    box-shadow: 0 8px 20px rgba(37, 99, 235, 0.3);
}

.chat-header-title {
    font-size: 1.6rem;
    font-weight: 800;
    color: var(--text-main);
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-top: 4px;
}

.chat-header-sub {
    font-size: 0.78rem;
    font-weight: 500;
    color: var(--text-dim);
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

/* ===== CHAT MESSAGES ===== */
[data-testid="stChatMessage"] {
    margin-bottom: 0.7rem;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

[data-testid="stChatMessage"] [data-testid="stChatMessageAvatar"],
[data-testid="stChatMessage"] [data-testid="stChatMessageAvatarUser"],
[data-testid="stChatMessage"] [data-testid="stChatMessageAvatarAssistant"] {
    width: 2.4rem !important;
    height: 2.4rem !important;
    min-width: 2.4rem !important;
    min-height: 2.4rem !important;
    flex: 0 0 2.4rem !important;
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

/* ===== CHAT INPUT ===== */
[data-testid="stChatInput"] textarea {
    background: var(--bg-surface) !important;
    color: var(--text-main) !important;
    border: 2px solid var(--border) !important;
    border-radius: 14px !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2) !important;
    min-height: 54px !important;
    font-weight: 400;
    font-size: 0.9rem;
    padding: 12px 16px !important;
    transition: border-color 0.2s ease !important;
}

[data-testid="stChatInput"] textarea:focus {
    border-color: var(--blue) !important;
    box-shadow: 0 4px 16px rgba(37, 99, 235, 0.15) !important;
}

[data-testid="stChatInput"] button {
    background: linear-gradient(135deg, var(--yellow) 0%, var(--gold) 100%) !important;
    color: #0F172A !important;
    border: 2px solid var(--yellow-border) !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    margin-left: 8px !important;
    font-size: 1.1rem !important;
}

[data-testid="stChatInput"] button:hover {
    box-shadow: 0 4px 16px rgba(250, 204, 21, 0.3) !important;
}

/* ===== NATIVE CHAT BUBBLES ===== */
/* User message — message à gauche de l'avatar, avatar à l'extrémité droite */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]),
[data-testid="stChatMessage"][aria-label*="user" i],
[data-testid="stChatMessage"]:has(.ae-bubble-user) {
    display: flex !important;
    flex-direction: row !important;
    justify-content: flex-end !important;
    align-items: flex-start !important;
    gap: 0.4rem !important;
    animation: aeSlideRight 0.3s ease both;
}

/* Content en order:1 → visuellement avant l'avatar (à sa gauche) */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"])
    [data-testid="stChatMessageContent"],
[data-testid="stChatMessage"][aria-label*="user" i]
    [data-testid="stChatMessageContent"],
[data-testid="stChatMessage"]:has(.ae-bubble-user)
    [data-testid="stChatMessageContent"] {
    order: 1 !important;
    flex: 1 1 0 !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    display: flex !important;
    justify-content: flex-end !important;
    padding: 0 !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"])
    [data-testid="stChatMessageContent"] *,
[data-testid="stChatMessage"][aria-label*="user" i]
    [data-testid="stChatMessageContent"] *,
[data-testid="stChatMessage"]:has(.ae-bubble-user)
    [data-testid="stChatMessageContent"] * {
    color: #FFFFFF !important;
}

/* Assistant message */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]),
[data-testid="stChatMessage"][aria-label*="assistant" i] {
    justify-content: flex-start !important;
    gap: 0.4rem !important;
    animation: aeSlideLeft 0.3s ease both;
}

[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"])
    [data-testid="stChatMessageContent"],
[data-testid="stChatMessage"][aria-label*="assistant" i]
    [data-testid="stChatMessageContent"] {
    background: var(--yellow-bg) !important;
    border: 1px solid var(--yellow-border) !important;
    border-radius: 4px 18px 18px 18px !important;
    color: #0F172A !important;
    display: inline-block;
    width: fit-content;
    max-width: min(78%, 760px);
    box-shadow: 0 4px 12px rgba(250, 204, 21, 0.15);
    padding: 0.7rem 0.9rem !important;
    font-weight: 400;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"])
    [data-testid="stChatMessageContent"] *,
[data-testid="stChatMessage"][aria-label*="assistant" i]
    [data-testid="stChatMessageContent"] * {
    color: #0F172A !important;
}

/* User avatar styling — order:2 → après le message (extrémité droite) */
[data-testid="stChatMessage"]:has(.ae-bubble-user) [data-testid="stChatMessageAvatar"],
[data-testid="stChatMessage"]:has(.ae-bubble-user) [data-testid="stChatMessageAvatarUser"],
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stChatMessageAvatar"],
[data-testid="stChatMessage"][aria-label*="user" i] [data-testid="stChatMessageAvatar"],
[data-testid="stChatMessage"][aria-label*="user" i] [data-testid="stChatMessageAvatarUser"] {
    order: 2 !important;
    flex-shrink: 0 !important;
    background: var(--blue) !important;
    border: 2px solid var(--blue-dark) !important;
    border-radius: 12px !important;
    color: #FFFFFF !important;
}

[data-testid="stChatMessage"]:has(.ae-bubble-user) [data-testid="stChatMessageAvatar"] svg,
[data-testid="stChatMessage"]:has(.ae-bubble-user) [data-testid="stChatMessageAvatarUser"] svg,
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stChatMessageAvatar"] svg {
    fill: #FFFFFF !important;
    color: #FFFFFF !important;
    stroke: #FFFFFF !important;
}

[data-testid="chatAvatarIcon-assistant"] {
    background: linear-gradient(135deg, var(--yellow) 0%, var(--gold) 100%) !important;
    border: 2px solid var(--yellow-border) !important;
    border-radius: 12px !important;
    padding: 8px !important;
    color: #0F172A !important;
}

[data-testid="chatAvatarIcon-assistant"] svg {
    fill: #0F172A !important;
    color: #0F172A !important;
    stroke: #0F172A !important;
}

/* ===== CUSTOM BUBBLE OVERRIDES ===== */
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

/* Force full width on intermediate containers inside user messages */
[data-testid="stChatMessage"]:has(.ae-bubble-user) [data-testid="stMarkdownContainer"],
[data-testid="stChatMessage"]:has(.ae-bubble-user) [data-testid="stElementContainer"],
[data-testid="stChatMessage"]:has(.ae-bubble-user) [data-testid="stVerticalBlock"],
[data-testid="stChatMessage"]:has(.ae-bubble-user) [data-testid="stHorizontalBlock"] {
    width: 100% !important;
}

/* ===== CUSTOM BUBBLE WRAPPERS ===== */
.ae-bubble {
    position: relative;
    display: inline-block;
    width: fit-content;
    max-width: min(78%, 760px);
    padding: 0.72rem 0.95rem;
    font-weight: 400;
    line-height: 1.5;
    word-wrap: break-word;
    font-size: 0.9rem;
}

.ae-bubble-wrap {
    width: fit-content;
    max-width: 100%;
    display: flex;
    margin-bottom: 2px;
}

.ae-bubble-wrap-user {
    width: 100% !important;
    justify-content: flex-end;
    margin-left: 0;
}

.ae-bubble-wrap-assistant {
    justify-content: flex-start;
    margin-right: auto;
}

.ae-bubble-user {
    background: var(--blue);
    border: 1px solid var(--blue-dark);
    border-radius: 18px 4px 18px 18px;
    color: #FFFFFF;
    box-shadow: 0 8px 20px rgba(37, 99, 235, 0.3);
    animation: aeSlideRight 0.3s ease both;
}

.ae-bubble-user::after {
    content: "";
    position: absolute;
    right: -8px;
    bottom: 12px;
    width: 0;
    height: 0;
    border-left: 9px solid var(--blue);
    border-top: 7px solid transparent;
    border-bottom: 7px solid transparent;
}

.ae-bubble-assistant {
    background: var(--yellow-bg);
    border: 1px solid var(--yellow-border);
    border-radius: 4px 18px 18px 18px;
    color: #0F172A;
    box-shadow: 0 4px 12px rgba(250, 204, 21, 0.12);
    animation: aeSlideLeft 0.3s ease both;
}

.ae-bubble-assistant::before {
    content: "";
    position: absolute;
    left: -8px;
    bottom: 12px;
    width: 0;
    height: 0;
    border-right: 9px solid var(--yellow-bg);
    border-top: 7px solid transparent;
    border-bottom: 7px solid transparent;
}

.ae-bubble p {
    margin: 0;
}

.ae-bubble * {
    color: inherit !important;
    background: transparent !important;
    font-weight: 500 !important;
}

@keyframes aeSlideLeft {
    from {
        opacity: 0;
        transform: translateX(-16px) translateY(3px);
    }
    to {
        opacity: 1;
        transform: translateX(0) translateY(0);
    }
}

@keyframes aeSlideRight {
    from {
        opacity: 0;
        transform: translateX(16px) translateY(3px);
    }
    to {
        opacity: 1;
        transform: translateX(0) translateY(0);
    }
}

/* ===== STREAMLIT NATIVE OVERRIDES ===== */
.stTextInput, .stTextArea {
    color: var(--text-main) !important;
}

div[data-testid="stMarkdownContainer"] p {
    color: var(--text-main);
}

/* ===== VEGA CHARTS ===== */
.vega-embed {
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    background: var(--bg-card) !important;
    padding: 8px !important;
}

.vega-embed text {
    fill: var(--text-muted) !important;
    font-weight: 500 !important;
}

/* ===== EXPANDER ===== */
.streamlit-expanderHeader {
    font-weight: 600 !important;
    color: var(--text-main) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    background: var(--bg-card) !important;
}

.streamlit-expanderContent {
    border: 1px solid var(--border) !important;
    border-top: none !important;
    border-radius: 0 0 10px 10px !important;
    background: var(--bg-card) !important;
}

/* ===== TABLES ===== */
table {
    border-collapse: collapse !important;
}

table th {
    background: var(--bg-surface) !important;
    color: var(--yellow) !important;
    font-weight: 600 !important;
    border: 1px solid var(--border) !important;
    padding: 10px 12px !important;
}

table td {
    background: var(--bg-card) !important;
    color: var(--text-main) !important;
    font-weight: 400 !important;
    border: 1px solid var(--border) !important;
    padding: 8px 12px !important;
}

/* ===== RESPONSIVE ===== */
@media (max-width: 900px) {
    .block-container {
        padding-top: 0.6rem !important;
        padding-left: 0.75rem !important;
        padding-right: 0.75rem !important;
    }

    .chat-header-avatar {
        width: 60px;
        height: 60px;
        font-size: 1.8rem;
    }

    .chat-header-title {
        font-size: 1.2rem;
    }
}

/* ===== USER PROFILE (Sidebar) ===== */
.user-profile {
    background: var(--gradient-accent-soft);
    border: 1px solid rgba(139, 92, 246, 0.3);
    border-radius: 14px;
    padding: 14px 16px;
    margin: 0 12px 14px 12px;
    display: flex;
    align-items: center;
    gap: 12px;
}

.user-profile-avatar {
    width: 44px;
    height: 44px;
    border-radius: 50%;
    background: var(--gradient-accent);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
    flex-shrink: 0;
    border: 2px solid rgba(139, 92, 246, 0.5);
}

.user-profile-name {
    font-size: 0.88rem;
    font-weight: 700;
    color: var(--text-main) !important;
}

.user-profile-role {
    font-size: 0.7rem;
    font-weight: 500;
    color: var(--purple-light) !important;
    margin-top: 2px;
}

/* ===== SAAS GREETING HEADER ===== */
.saas-greeting {
    padding: 4px 0 16px 0;
}

.saas-greeting-hi {
    font-size: 1.65rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    line-height: 1.2;
    color: var(--text-main);
}

.saas-greeting-name {
    background: var(--gradient-accent);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.saas-greeting-sub {
    font-size: 0.85rem;
    font-weight: 400;
    color: var(--text-muted);
    margin-top: 4px;
}

/* ===== SAAS BANNER ===== */
.saas-banner {
    background: var(--gradient-accent-soft);
    border: 1px solid rgba(139, 92, 246, 0.3);
    border-radius: 16px;
    padding: 18px 22px;
    margin-bottom: 20px;
}

.saas-banner-tag {
    display: inline-block;
    background: rgba(139, 92, 246, 0.2);
    border: 1px solid var(--purple-light);
    border-radius: 6px;
    padding: 2px 10px;
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    color: var(--purple-light) !important;
    margin-bottom: 8px;
}

.saas-banner-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--text-main) !important;
    margin-bottom: 4px;
}

.saas-banner-desc {
    font-size: 0.82rem;
    font-weight: 400;
    color: var(--text-muted) !important;
}

/* ===== FILTER TABS (visual) ===== */
.saas-filter-bar {
    display: flex;
    gap: 8px;
    padding: 4px 0 16px 0;
    flex-wrap: wrap;
}

.saas-filter-tab {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 5px 16px;
    font-size: 0.78rem;
    font-weight: 600;
    color: var(--text-muted) !important;
    cursor: default;
    user-select: none;
    display: inline-block;
}

.saas-filter-tab-active {
    background: var(--gradient-accent-soft);
    border-color: var(--purple-light);
    color: var(--purple-light) !important;
}

/* ===== SETTINGS PAGE ===== */
.settings-section-header {
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--text-dim) !important;
    padding-bottom: 10px;
    margin-bottom: 14px;
    border-bottom: 1px solid var(--border);
}

.danger-zone-header {
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #F87171 !important;
    padding-bottom: 10px;
    margin-bottom: 14px;
    border-bottom: 1px solid rgba(239, 68, 68, 0.3);
}

/* ===== AI COLLABORATION SECTION ===== */
.collab-section-title {
    font-size: 0.98rem;
    font-weight: 700;
    color: var(--text-main) !important;
    margin-bottom: 3px;
}

.collab-section-sub {
    font-size: 0.78rem;
    color: var(--text-muted) !important;
    margin-bottom: 14px;
}

.collab-chat-area {
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin-bottom: 14px;
}

.collab-bubble {
    padding: 10px 14px;
    border-radius: 12px;
    font-size: 0.87rem;
    line-height: 1.55;
    max-width: 90%;
}

.collab-bubble-user {
    background: rgba(37, 99, 235, 0.14);
    border: 1px solid rgba(37, 99, 235, 0.28);
    border-radius: 12px 3px 12px 12px;
    margin-left: auto;
}

.collab-bubble-ai {
    background: var(--gradient-accent-soft);
    border: 1px solid rgba(139, 92, 246, 0.28);
    border-radius: 3px 12px 12px 12px;
}

.collab-label {
    font-size: 0.65rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    margin-bottom: 4px;
}

.collab-label-user { color: #60A5FA !important; }
.collab-label-ai   { color: var(--purple-light) !important; }

.collab-suggestions {
    display: flex;
    flex-direction: column;
    gap: 7px;
    margin-top: 8px;
}

.collab-suggestion {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid var(--border);
    border-left: 3px solid var(--purple-light);
    border-radius: 0 10px 10px 0;
    padding: 9px 14px;
    font-size: 0.83rem;
    font-weight: 500;
    color: var(--text-main) !important;
}

/* ===== FOOTER ===== */
.ae-footer {
    position: fixed;
    bottom: 6px;
    left: 0;
    right: 0;
    text-align: center;
    font-size: 0.62rem;
    font-weight: 500;
    color: var(--text-dim);
    pointer-events: none;
    z-index: 9999;
}

/* ===== BADGE ===== */
.ae-badge {
    display: inline-block;
    background: rgba(20, 184, 166, 0.15);
    border: 1px solid var(--teal);
    border-radius: 8px;
    padding: 3px 12px;
    font-weight: 700;
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--teal);
}

/* ===== SPINNER ===== */
.stSpinner {
    border-color: var(--yellow) !important;
    border-top-color: transparent !important;
}

div[data-testid="stStatusWidget"] {
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    background: var(--bg-card) !important;
    font-weight: 500 !important;
    color: var(--text-main) !important;
}

/* ===== STREAMLIT NATIVE OVERRIDES ===== */
.stTextInput, .stTextArea {
    color: var(--text-main) !important;
}

div[data-testid="stMarkdownContainer"] p {
    color: var(--text-main);
}

/* Checkbox / Toggle */
div[data-baseweb="checkbox"] span,
div[data-baseweb="checkbox"] label {
    color: var(--text-main) !important;
}

/* Slider */
div[data-baseweb="slider"] div {
    color: var(--text-main) !important;
}

/* Tab bar */
button[data-baseweb="tab"] {
    color: var(--text-muted) !important;
    border-bottom: 2px solid transparent !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: var(--yellow) !important;
    border-bottom-color: var(--yellow) !important;
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


# ================= SESSION STATE =================
if "page" not in st.session_state:
    st.session_state.page = "💬 Assistant"
if "dashboard_page" not in st.session_state:
    st.session_state.dashboard_page = " Vue globale"
if "collab_chat" not in st.session_state:
    st.session_state.collab_chat = {}


def set_page(p: str):
    st.session_state.page = p

def set_dashboard_page(p: str):
    st.session_state.dashboard_page = p


# ================= SIDEBAR =================
with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <img class="sidebar-avatar" src="ui/aelon_avatar.png" alt="AELON" />
            <div class="sidebar-title">AELON</div>
            <div class="sidebar-subtitle">Banking Assistant</div>
        </div>
        <hr class="sidebar-sep" />
        """,
        unsafe_allow_html=True,
    )


    st.markdown('<div class="sidebar-nav-label">▼ Navigation</div>', unsafe_allow_html=True)

    # Main navigation
    chat_active = st.session_state.page == "💬 Assistant"
    dash_active = st.session_state.page == "📊 Dashboard"

    col1, col2 = st.columns(2)
    with col1:
        if st.button("💬 Assistant", use_container_width=True,
                     type="primary" if chat_active else "secondary"):
            set_page("💬 Assistant")
    with col2:
        if st.button("📊 Dashboard", use_container_width=True,
                     type="primary" if dash_active else "secondary"):
            set_page("📊 Dashboard")

    mode = "Utilisateur" if st.session_state.page == "💬 Assistant" else "Admin"

    if mode == "Admin":
        st.markdown('<hr class="sidebar-sep" />', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-nav-label">▼ Modules</div>', unsafe_allow_html=True)

        dash_pages = [
            "Vue globale",
            "Analyse des sentiments",
            "Analyse des escalades (L0 / L1)",
            "Analyse des fraudes",
            "Analyse des requêtes / catégories",
            "Paramètres",
        ]

        current_dash = st.session_state.dashboard_page

        for dp in dash_pages:
            is_active = dp == current_dash
            if st.button(dp, use_container_width=True,
                         type="primary" if is_active else "secondary",
                         key=f"dash_{dp}"):
                set_dashboard_page(dp)

    st.markdown('<hr class="sidebar-sep" />', unsafe_allow_html=True)
    if mode == "Utilisateur":
        st.markdown('<div class="sidebar-nav-label">▼ Messages rapides</div>', unsafe_allow_html=True)
        _quick_messages = [
            "Comment signaler une fraude ?",
            "J'ai perdu ma carte bancaire",
            "Comment effectuer un virement ?",
            "Comment contacter un conseiller ?",
        ]
        for _i, _qm in enumerate(_quick_messages):
            if st.button(_qm, use_container_width=True, key=f"quick_msg_{_i}"):
                st.session_state.quick_message = _qm
        st.markdown('<hr class="sidebar-sep" />', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-footer">AELON — 2026</div>', unsafe_allow_html=True)

# ================= STORAGE =================
INTERACTIONS_FILE = "interactions.json"

def load_data():
    if Path(INTERACTIONS_FILE).exists():
        return json.load(open(INTERACTIONS_FILE))
    return []

def save_data(data):
    json.dump(data, open(INTERACTIONS_FILE, "w"), indent=2)


def render_chat_bubble(role: str, content: str) -> None:
    """Render chat content with custom bubbles matching the project style."""
    bubble_class = "ae-bubble-user" if role == "user" else "ae-bubble-assistant"
    wrap_class = "ae-bubble-wrap-user" if role == "user" else "ae-bubble-wrap-assistant"
    safe_content = html.escape(str(content)).replace("\n", "<br>")
    st.markdown(
        (
            f'<div class="ae-bubble-wrap {wrap_class}">'
            f'<div class="ae-bubble {bubble_class}">{safe_content}</div>'
            f'</div>'
        ),
        unsafe_allow_html=True,
    )


# ================= DASHBOARD COLLAB =================
@st.cache_resource
def get_dashboard_llm() -> AzureChatLLM:
    return AzureChatLLM()


def _collab_ask(llm: AzureChatLLM, system_prompt: str, history: list, question: str) -> str:
    msgs = [{"role": "system", "content": system_prompt}]
    for m in history[-6:]:
        msgs.append(m)
    msgs.append({"role": "user", "content": question})
    resp = llm.client.chat.completions.create(
        model=llm.deployment,
        messages=msgs,
        temperature=0.35,
        max_tokens=400,
    )
    return resp.choices[0].message.content.strip()


def render_collab_section(page_key: str, context: str, suggestions: list) -> None:
    """Inline AI collaboration chat + suggestions for a dashboard page."""
    st.markdown("---")
    st.markdown(
        '<div class="collab-section-title">💬 Analyse avec l\'assistant IA</div>'
        '<div class="collab-section-sub">Posez vos questions sur les données pour obtenir des recommandations ciblées.</div>',
        unsafe_allow_html=True,
    )

    chat_key = f"collab_{page_key}"
    if chat_key not in st.session_state.collab_chat:
        st.session_state.collab_chat[chat_key] = []
    history = st.session_state.collab_chat[chat_key]

    if history:
        bubbles = '<div class="collab-chat-area">'
        for msg in history:
            safe = html.escape(msg["content"]).replace("\n", "<br>")
            if msg["role"] == "user":
                bubbles += (
                    f'<div class="collab-bubble collab-bubble-user">'
                    f'<div class="collab-label collab-label-user">👤 Admin</div>{safe}</div>'
                )
            else:
                bubbles += (
                    f'<div class="collab-bubble collab-bubble-ai">'
                    f'<div class="collab-label collab-label-ai">🤖 IA</div>{safe}</div>'
                )
        bubbles += '</div>'
        st.markdown(bubbles, unsafe_allow_html=True)

    with st.form(key=f"collab_form_{page_key}", clear_on_submit=True):
        user_q = st.text_input(
            "Question",
            placeholder="Ex : Quelles sont les causes d\'escalade ? Que devrions-nous améliorer ?",
            label_visibility="collapsed",
        )
        submitted = st.form_submit_button("💬 Envoyer", use_container_width=True)

    if submitted and user_q.strip():
        system_prompt = (
            "Tu es un assistant IA expert en analyse de données bancaires pour le système AELON. "
            f"Contexte du tableau de bord : {context} "
            "Analyse les données, explique les insights, identifie les causes racines et propose des actions. "
            "Réponds en français en 3-4 phrases max. Pose une question de suivi si pertinent."
        )
        try:
            _llm = get_dashboard_llm()
            with st.spinner("L'IA analyse..."):
                ai_response = _collab_ask(_llm, system_prompt, history, user_q.strip())
        except Exception as exc:
            ai_response = f"⚠️ Erreur lors de l'analyse : {exc}"

        st.session_state.collab_chat[chat_key].append({"role": "user", "content": user_q.strip()})
        st.session_state.collab_chat[chat_key].append({"role": "assistant", "content": ai_response})
        st.rerun()

    sug_html = "".join(
        f'<div class="collab-suggestion">&rarr;&nbsp;{html.escape(s)}</div>'
        for s in suggestions
    )
    st.markdown(
        f'<div style="font-size:0.8rem;font-weight:700;margin:14px 0 8px 0;color:var(--text-dim)">'
        f'💡 Actions suggérées</div>'
        f'<div class="collab-suggestions">{sug_html}</div>',
        unsafe_allow_html=True,
    )


# ================= ADMIN =================
if st.session_state.page == "📊 Dashboard":
    import pandas as pd
    import altair as alt

    st.markdown(
        """
        <div class="saas-greeting">
            <div class="saas-greeting-hi">Bonjour, <span class="saas-greeting-name">Admin</span> &#x1F44B;</div>
            <div class="saas-greeting-sub">Bienvenue sur votre tableau de bord AELON</div>
        </div>
        <div class="saas-banner">
            <div class="saas-banner-tag">&#x26A1; Live</div>
            <div class="saas-banner-title">Centre de D&#233;cision M&#233;tier</div>
            <div class="saas-banner-desc">Analysez les tendances, comprenez les causes et appliquez des recommandations concr&#232;tes.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    data = load_data()
    if not data:
        st.warning("⚠️ Pas de données disponibles. Lancez quelques conversations en mode Assistant d'abord.")
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
    st.sidebar.markdown('<div class="sidebar-nav-label">▼ Filtres</div>', unsafe_allow_html=True)

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

    dp = st.session_state.dashboard_page

    if dp == "Vue globale":
        st.subheader("Vue globale")

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
                    scale=alt.Scale(domain=["L0", "L1", "blocked"], range=["#2563EB", "#14B8A6", "#F87171"]),
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
        render_collab_section(
            "vue_globale",
            f"Vue globale — {total} interactions, escalade {escalation_rate:.1f}%, fraude moyenne {avg_fraud:.1f}, sentiment négatif {neg_rate:.1f}%, catégorie principale : {top_cat}. Analyse : {analysis}",
            [
                "Automatiser les réponses sur la catégorie dominante",
                "Analyser les pics d'escalade par plage horaire",
                "Renforcer la surveillance proactive des risques fraude",
            ],
        )

    elif dp == "Analyse des sentiments":
        st.subheader("Analyse des sentiments")

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
            analysis = "Un nombre important d'interactions est associé à un sentiment négatif, ce qui peut indiquer des problèmes dans l'expérience client."
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
        render_collab_section(
            "sentiments",
            f"Analyse des sentiments — taux négatif {neg_rate:.1f}%. Analyse : {analysis}",
            [
                "Améliorer les réponses sur les cas de frustration fréquents",
                "Créer des scripts de réponse pour les sujets sensibles",
                "Mettre en place un suivi des sentiments en temps réel",
            ],
        )

    elif dp == "Analyse des escalades (L0 / L1)":
        st.subheader("Analyse des escalades (L0 / L1)")

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
                    scale=alt.Scale(domain=["L0", "L1", "blocked"], range=["#2563EB", "#14B8A6", "#F87171"]),
                    legend=None,
                ),
                tooltip=["agent:N", "count:Q"],
            )
            .properties(height=320)
        )
        st.altair_chart(escalation_chart, use_container_width=True)

        l1_rate = float((filtered["agent"] == "L1").mean() * 100)
        if l1_rate >= 30:
            analysis = "Le taux d'escalade est élevé, ce qui suggère que les requêtes ne sont pas suffisamment traitées au niveau L0."
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
        render_collab_section(
            "escalades",
            f"Analyse des escalades — taux L1 {l1_rate:.1f}%. Analyse : {analysis}",
            [
                "Enrichir la base de connaissances L0 sur les motifs d'escalade",
                "Revoir le routage automatique des requêtes complexes",
                "Mettre en place des seuils d'alerte pour le taux d'escalade",
            ],
        )

    elif dp == "Analyse des fraudes":
        st.subheader("Analyse des fraudes")

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
        render_collab_section(
            "fraudes",
            f"Analyse des fraudes — taux fraude {fraud_rate:.1f}%, score moyen {filtered['fraud_score'].mean():.1f}. Analyse : {analysis}",
            [
                "Affiner les règles de détection sur les patterns récurrents",
                "Mettre en place des alertes temps réel pour les scores élevés",
                "Analyser les faux positifs pour réduire les blocages inutiles",
            ],
        )

    elif dp == "Analyse des requêtes / catégories":
        st.subheader("Analyse des requêtes / catégories")

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
        render_collab_section(
            "categories",
            f"Analyse des catégories — top catégorie {top_ratio:.1f}% du volume. Analyse : {analysis}",
            [
                "Automatiser les réponses sur les 3 catégories les plus fréquentes",
                "Créer des workflows dédiés par catégorie prioritaire",
                "Optimiser les temps de réponse sur les catégories à fort volume",
            ],
        )

    elif dp == "⚙️ Paramètres":
        st.subheader("⚙️ Paramètres")

        # ── Profil ──────────────────────────────────────
        st.markdown('<div class="settings-section-header">👤 Profil</div>', unsafe_allow_html=True)
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.text_input("Nom d'affichage", value="Admin", key="settings_name")
        with col_p2:
            st.text_input("Email", value="admin@aelon.ai", key="settings_email")
        st.button("💾 Sauvegarder le profil", key="settings_save")

        st.markdown("---")

        # ── Abonnement ──────────────────────────────────
        st.markdown('<div class="settings-section-header">💳 Abonnement</div>', unsafe_allow_html=True)
        col_s1, col_s2 = st.columns([3, 1])
        with col_s1:
            st.markdown('<div class="ae-badge">✅ Plan Pro — Actif</div>', unsafe_allow_html=True)
            st.markdown(
                '<p style="margin-top:8px;font-size:0.85rem">Renouvellement : 25 juillet 2026 &nbsp;·&nbsp; Facturation mensuelle</p>',
                unsafe_allow_html=True,
            )
        with col_s2:
            st.button("🔄 Gérer", key="settings_plan")

        st.markdown("---")

        # ── Zone de danger ───────────────────────────────
        st.markdown('<div class="danger-zone-header">⚠️ Zone de danger</div>', unsafe_allow_html=True)
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.button("🗑️ Supprimer toutes les données", key="settings_delete", use_container_width=True)
        with col_d2:
            st.button("📞 Contacter le support", key="settings_support", use_container_width=True)

    if dp != "⚙️ Paramètres":
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
            "content": "👋 Bonjour, je suis **AELON**, votre assistant bancaire intelligent.\n\nComment puis-je vous aider aujourd'hui ?"
        })

        #  message sécurité
        st.session_state.messages.append({
            "role": "assistant",
            "content": "🔒 **Important :** Ne partagez jamais vos informations sensibles (mot de passe, code OTP, numéro de carte)."
        })

    # ===== HEADER =====
    st.markdown(
        """
        <div class="chat-header">
            <img class="chat-header-avatar" src="ui/aelon_avatar.png" alt="AELON" />
            <div class="chat-header-title">AELON</div>
            <div class="chat-header-sub">Banking Assistant</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")


    # ===== CHAT HISTORY =====
    for msg in st.session_state.messages:
        if msg["role"] == "assistant":
            with st.chat_message("assistant", avatar=AELON_AVATAR_BYTES):
                render_chat_bubble(msg["role"], msg["content"])
        else:
            with st.chat_message(msg["role"]):
                render_chat_bubble(msg["role"], msg["content"])

    # ===== INPUT =====
    user_input = st.chat_input("Écrivez votre message...")

    # Messages rapides depuis la sidebar
    _quick = st.session_state.get("quick_message")
    if _quick and not user_input:
        user_input = _quick
        del st.session_state["quick_message"]

    st.markdown(
        '<div class="ae-footer">'
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
                with st.chat_message("assistant", avatar=AELON_AVATAR_BYTES):
                    render_chat_bubble("assistant", escalation_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": escalation_msg
                })

        # ===== AFFICHAGE =====
        with st.chat_message("assistant", avatar=AELON_AVATAR_BYTES):
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
