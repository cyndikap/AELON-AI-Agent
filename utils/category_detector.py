# -*- coding: utf-8 -*-
"""
Category detector for banking support queries.
Classifies user queries into predefined categories based on keywords.
"""

CATEGORY_KEYWORDS = {
    "fraude": [
        "fraude", "arnaque", "suspect", "vol", "hack", "pirate",
        "inconnu", "non autorisé", "je ne reconnais pas", "phishing",
        "usurpation", "escroquerie", "activité suspecte"
    ],
    "connexion": [
        "connexion", "connecter", "login", "mot de passe", "password",
        "identifiant", "accès", "compte bloqué", "verrouillé", "otp",
        "code secret", "authentification", "session", "déconnecté",
        "réinitialiser", "reinitialiser", "réinitialisation"
    ],
    "carte": [
        "carte", "visa", "mastercard", "cb", "carte bancaire",
        "carte refusée", "carte bloquée", "plafond", "opposition",
        "retrait", "distributeur", "guichet automatique"
    ],
    "paiement": [
        "paiement", "payer", "virement", "transfer", "transfert", "transaction",
        "montant", "débit", "prélèvement", "facture", "reçu",
        "virement échoué", "paiement refusé", "solde", "règlement"
    ],
}

CATEGORY_LABELS = {
    "connexion": "🔐 Connexion",
    "paiement": "💸 Paiement",
    "carte": "💳 Carte bancaire",
    "fraude": "🚨 Fraude",
    "autre": "📌 Autre",
}


def detect_category(query: str) -> str:
    """
    Detect the category of a banking support query.

    Args:
        query: The user's query text.

    Returns:
        Category string: 'connexion', 'paiement', 'carte', 'fraude', or 'autre'.
    """
    if not query:
        return "autre"

    text = query.lower()

    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            return category

    return "autre"


def get_category_label(category: str) -> str:
    """Return a human-readable label for a category."""
    return CATEGORY_LABELS.get(category, "📌 Autre")
