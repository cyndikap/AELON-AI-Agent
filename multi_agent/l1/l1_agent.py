# -*- coding: utf-8 -*-

from typing import Dict, Any
from global_prompt import prepend


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
            user_language = context.get("user_language", "en")
        else:
            user_query = str(context)
            user_language = "en"

        # 2. récupérer les données (RAG)
        retrieved_data = []
        if self.retriever:
            try:
                retrieved_data = self.retriever.search(user_query)
            except Exception:
                pass

        # 3. construire le prompt
        prompt = f"""
        You are an expert L1 banking support advisor.

        CRITICAL: You MUST reply in the EXACT same language as the user's question.
        Target language code: {user_language}
        Do NOT translate or switch language under any circumstances.
        Start with a short professional introduction in that same language.

        Client problem:
        {user_query}

        Available data:
        {retrieved_data}

        Provide:
        - a clear diagnosis
        - a recommended solution
        - concrete steps to resolve the issue
        """

        # 4. appel LLM
        full_response = self.llm(prepend(prompt))

        # 6. retour structuré
        return {
            "summary": full_response,
            "technical_analysis": full_response,
            "confidence": 0.85,
            "related_logs": retrieved_data
        }