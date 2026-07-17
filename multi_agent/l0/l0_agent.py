# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-

import os
from dotenv import load_dotenv
from multi_agent.l0.knowledge_base import KnowledgeBase
from multi_agent.l0.memory import L0Memory
from multi_agent.l0.azure_kb import AzureKB
from global_prompt import prepend
load_dotenv()

AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
AZURE_SEARCH_INDEX = os.getenv("AZURE_AI_SEARCH_INDEX_NAME")
AZURE_SEARCH_KEY      = os.getenv("AZURE_AI_SEARCH_API_KEY")


class L0Agent:
    """
    L0Agent – knowledge-first self-service agent.
    NO infrastructure dependencies.
    """

    def __init__(self, llm, kb_path: str):
        self.llm = llm
        self.kb = AzureKB(
            endpoint=AZURE_SEARCH_ENDPOINT,
            index_name=AZURE_SEARCH_INDEX,
            api_key=AZURE_SEARCH_KEY
        )
        
        self.memory = L0Memory()

    def handle(self, user_query, tone_hint=None, context=None):
        chunks = self.kb.search(user_query)
        context_text = "\n\n".join([chunk["text"] for chunk in chunks]) if chunks else ""
        memory_hits = self.memory.search(user_query)

        llm_output = self.llm(prepend(f"""
    Tu es un agent de support bancaire niveau L0.
    Ton de réponse attendu : {tone_hint}.

    Utilise uniquement le contexte ci-dessous pour répondre à la question.
    Si le contexte ne contient pas assez d'information, réponds : "J'ai besoins de plus d'informations".
    Réponds dans la même langue que la user_query.

    Contexte :
    {context_text}

    Question :
    {user_query}
    """))


        normalized = llm_output.lower()
        unknown_phrases = ["je ne sais pas", "i don't know", "i do not know", "ich weiß nicht", "no lo sé", "não sei", "不知道"]
        is_unknown = any(p in normalized for p in unknown_phrases)

        if chunks and not is_unknown:
            result = {
                "decision": "answer",
                "response": llm_output,
                "confidence": 0.8,
            }
        else:
            result = {
                "decision": "escalate",
                "reason": llm_output,
                "context": {
                    "user_query": user_query,
                    "l0_reasoning": llm_output,
                    "kb_used": bool(chunks),
                    "memory_matches": memory_hits,
                },
            }

        self.memory.add({
            "query": user_query,
            "decision": result["decision"],
            "response": llm_output,
        })

        return result
