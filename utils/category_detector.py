# -*- coding: utf-8 -*-

"""Keyword-based category detection for customer support queries."""

CATEGORY_KEYWORDS = {
    "connexion": [
        "mot de passe", "password", "accès", "connexion", "login", "compte",
        "connecter", "identifiant", "authentification", "otp", "session",
        "déconnecté", "verrouillé", "code secret",
    ],
    "paiement": [
        "paiement", "virement", "transfert", "transaction", "payer", "régler",
        "prélèvement", "solde", "facture", "remboursement",
        "montant", "somme", "argent", "euros",
    ],
    "fraude": [
        "fraude", "suspect", "volé", "voler", "arnaque", "phishing",
        "frauduleux", "fraudulent", "piratage", "hacké", "usurpation",
        "escroquerie", "inconnu", "non autorisé",
    ],
    "carte": [
        "carte", "cb", "visa", "mastercard", "retrait", "distributeur",
        "plafond", "bloquée", "bloqué", "désactivée", "puce",
        "sans contact", "tpe",
    ],
}

CATEGORY_COLORS = {
    "connexion": "#3B82F6",   # blue
    "paiement":  "#10B981",   # green
    "fraude":    "#EF4444",   # red
    "carte":     "#F59E0B",   # amber
    "autre":     "#6B7280",   # gray
}

CATEGORY_ICONS = {
    "connexion": "🔐",
    "paiement":  "💸",
    "fraude":    "🚨",
    "carte":     "💳",
    "autre":     "❓",
}


def detect_category(query: str) -> str:
    """Return the best-matching category for *query* based on keywords.

    Returns one of: 'connexion', 'paiement', 'fraude', 'carte', 'autre'.
    """
    if not query:
        return "autre"
    query_lower = query.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in query_lower:
                return category
    return "autre"
