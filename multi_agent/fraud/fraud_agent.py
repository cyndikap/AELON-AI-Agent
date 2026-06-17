# -*- coding: utf-8 -*-

import os
from dotenv import load_dotenv

load_dotenv()

FRAUD_PATTERNS = [
    "mot de passe", "password", "code otp", "code secret", "pin",
    "numéro de carte", "card number", "cvv", "date d'expiration",
    "je suis conseiller", "je suis agent", "i am your advisor",
    "virement urgent", "urgent transfer", "compte bloqué",
    "cliquez sur ce lien", "click this link", "vérifiez votre compte",
    "verify your account", "suspicion de fraude", "fraud detected"
]


class FraudAgent:
    """
    Détection de fraude enrichie avec score
    """

    def __init__(self, llm=None):
        self.llm = llm

    def analyze(self, input_data):

        score = 0
        reasons = []

        # TEXTE UTILISATEUR (TA LOGIQUE EXISTANTE)
        if isinstance(input_data, str):

            text = input_data.lower()

            suspicious_keywords = [
                "fraud", "hack", "suspicious",
                "unknown payment", "paiement inconnu",
                "je ne reconnais pas"
            ]

            if any(k in text for k in suspicious_keywords):
                score += 50
                reasons.append("Mots-clés suspects détectés")

            # AJOUT scoring
            if "urgent" in text:
                score += 10
                reasons.append("Urgence détectée")

        # DONNÉES TRANSACTION (NOUVEAU)
        elif isinstance(input_data, dict):

            amount = float(input_data.get("Amount", 0))

            if amount > 10000:
                score += 50
                reasons.append("Montant très élevé")

            elif amount > 3000:
                score += 30
                reasons.append("Montant élevé")

        # NORMALISATION
        score = min(score, 100)

        #  classification (AJOUT)
        if score >= 70:
            risk_level = "HIGH"
            is_fraud = True
        elif score >= 40:
            risk_level = "MEDIUM"
            is_fraud = False
        else:
            risk_level = "LOW"
            is_fraud = False

        return {
            "is_fraud": is_fraud,
            "score": score,          
            "risk_level": risk_level, 
            "reasons": reasons       
        }
