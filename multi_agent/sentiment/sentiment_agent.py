# -*- coding: utf-8 -*-

URGENT_KEYWORDS = [
    "urgent", "immédiatement", "immediately", "bloqué", "blocked",
    "impossible", "plus accès", "no access", "dringend", "sofort",
    "argent", "money", "virement", "transfer", "carte bloquée"
]


class SentimentAgent:
    """
    SentimentAgent — analyse le ton émotionnel avant L0.
    Retourne : sentiment, urgency_level, tone_hint pour adapter la réponse.
    """

    def __init__(self, llm):
        self.llm = llm

    def analyze(self, user_query: str) -> dict:
        keyword_urgent = any(k in user_query.lower() for k in URGENT_KEYWORDS)

        llm_output = self.llm(f"""
Tu es un agent d'analyse de sentiment pour un support bancaire.

Analyse le message client suivant et retourne uniquement un JSON :
{{
  "sentiment": "positive" | "neutral" | "frustrated" | "angry",
  "urgency_level": "low" | "medium" | "high",
  "tone_hint": "empathique et rassurant" | "neutre et informatif" | "calme et prioritaire",
  "summary": "résumé en une phrase de l'état émotionnel du client"
}}

Message : {user_query}
""")

        sentiment = "neutral"
        for s in ("positive", "frustrated", "angry"):
            if f'"sentiment": "{s}"' in llm_output.lower():
                sentiment = s
                break

        urgency = "high" if keyword_urgent else "low"
        if '"urgency_level": "high"' in llm_output.lower():
            urgency = "high"
        elif '"urgency_level": "medium"' in llm_output.lower() and urgency != "high":
            urgency = "medium"

        tone_hint = "neutral and informative"
        if sentiment in ("frustrated", "angry") or urgency == "high":
            tone_hint = "empathetic and reassuring"
        elif urgency == "medium":
            tone_hint = "calm and high-priority"

        return {
            "sentiment": sentiment,
            "urgency_level": urgency,
            "tone_hint": tone_hint,
            "raw": llm_output,
        }
