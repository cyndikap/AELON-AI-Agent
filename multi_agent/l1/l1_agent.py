# -*- coding: utf-8 -*-

from typing import Dict, Any


class L1Agent:
    """
    L1Agent – diagnostic technique enrichi par les données (RAG simple)
    """

    def __init__(self, llm, retriever=None):
        self.llm = llm
        self.retriever = retriever

    def diagnose_from_escalation(self, context):
        # 1. récupérer la requête utilisateur
        if isinstance(context, dict):
            user_query = context.get("user_query", "")
        else:
            user_query = str(context)

        # 2. récupérer les données (RAG)
        retrieved_data = []
        if self.retriever:
            try:
                retrieved_data = self.retriever.search(user_query)
            except Exception:
                pass

        # 3. construire le prompt
        prompt = f"""
        Tu es un expert en support bancaire de niveau L1.

        Problème client :
        {user_query}

        Données disponibles :
        {retrieved_data}

        Donne :
        - un diagnostic clair
        - une solution recommandée
        - des étapes concrètes pour résoudre le problème

        Réponds dans la même langue que la question.
        """

        # 4. appel LLM
        response = self.llm(prompt)

        # 5. retour structuré
        return {
            "summary": response,
            "technical_analysis": response,
            "confidence": 0.85,
            "related_logs": retrieved_data
        }