# -*- coding: utf-8 -*-

"""Keyword-based category detection for customer support queries."""

CATEGORY_KEYWORDS = {
    "connexion": [
        "mot de passe", "password", "acces", "accès", "connexion", "login", "compte",
        "connecter", "identifiant", "authentification", "otp", "session",
        "deconnecte", "déconnecté", "verrouille", "verrouillé", "code secret",
        "reinitialiser", "réinitialiser", "réinitialisation", "compte bloque", "compte bloqué",
    ],
    "paiement": [
        "paiement", "transaction", "payer", "regler", "régler",
        "prelevement", "prélèvement", "solde", "facture", "remboursement", "recu", "reçu",
        "montant", "somme", "argent", "euros", "debit", "débit", "paiement refuse", "paiement refusé",
    ],
    "virement": [
        "virement", "sepa", "beneficiaire", "bénéficiaire", "iban", "swift", "international",
        "annuler un virement", "virement permanent", "virement ponctuel", "virement instantane", "virement instantané",
        "transfert", "transfer", "virement echoue", "virement échoué",
    ],
    "fraude": [
        "fraude", "suspect", "vole", "volé", "voler", "arnaque", "phishing",
        "frauduleux", "fraudulent", "piratage", "hack", "hacke", "hacké", "pirate", "usurpation",
        "escroquerie", "inconnu", "non autorise", "non autorisé", "activite suspecte", "activité suspecte",
        "je ne reconnais pas",
    ],
    "carte": [
        "carte", "cb", "visa", "mastercard", "carte bancaire", "carte refusee", "carte refusée",
        "retrait", "distributeur", "guichet automatique", "plafond", "opposition",
        "bloquee", "bloquée", "bloque", "bloqué", "desactivee", "désactivée", "puce",
        "sans contact", "tpe",
    ],
    "rgpd": [
        "rgpd", "donnees personnelles", "données personnelles", "droit d'acces", "droit d'accès",
        "suppression de mes donnees", "suppression de mes données", "portabilite", "portabilité",
        "responsable du traitement", "consentement", "privacy", "confidentialite", "confidentialité",
    ],
    "kyc": [
        "kyc", "piece d'identite", "pièce d'identité", "justificatif de domicile", "connaissance client",
        "profil client", "mise a jour des informations", "mise à jour des informations", "dossier incomplet",
        "verification d'identite", "vérification d'identité",
    ],
    "conformite": [
        "acpr", "conformite", "conformité", "blanchiment", "lcb-ft", "tracfin", "declaration de soupcon",
        "déclaration de soupçon", "obligations reglementaires", "obligations réglementaires", "controle interne", "contrôle interne",
    ],
}

CATEGORY_COLORS = {
    "connexion": "#3B82F6",
    "paiement": "#10B981",
    "virement": "#0EA5E9",
    "fraude": "#EF4444",
    "carte": "#F59E0B",
    "rgpd": "#8B5CF6",
    "kyc": "#14B8A6",
    "conformite": "#F97316",
    "autre": "#6B7280",
}

CATEGORY_ICONS = {
    "connexion": "🔐",
    "paiement": "💸",
    "virement": "🏦",
    "fraude": "🚨",
    "carte": "💳",
    "rgpd": "🛡️",
    "kyc": "🪪",
    "conformite": "⚖️",
    "autre": "❓",
}

CATEGORY_LABELS = {
    "connexion": "🔐 Connexion",
    "paiement": "💸 Paiement",
    "virement": "🏦 Virement",
    "carte": "💳 Carte bancaire",
    "fraude": "🚨 Fraude",
    "rgpd": "🛡️ RGPD",
    "kyc": "🪪 KYC",
    "conformite": "⚖️ Conformité",
    "autre": "📌 Autre",
}


def detect_category(query: str) -> str:
    """Return the best-matching category for *query* based on keywords."""
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
