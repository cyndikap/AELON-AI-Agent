#L’orchestrateur joue un rôle central dans le système en coordonnant les différents agents 
# et en orchestrant le flux de traitement des requêtes clients, 
# #depuis leur analyse jusqu’à la génération de la réponse finale.



import json
import re
from dotenv import load_dotenv
load_dotenv()

from azure_chat_llm import AzureChatLLM
from multi_agent.l0.l0_agent import L0Agent
from multi_agent.l1.l1_agent import L1Agent
from multi_agent.fraud.fraud_agent import FraudAgent
from multi_agent.sentiment.sentiment_agent import SentimentAgent
from multi_agent.compliance.compliance_agent import ComplianceAgent
from multi_agent.privacy.privacy_agent import PrivacyAgent

from multi_agent.data_access.databricks_connector import DatabricksConnector
from multi_agent.retrieval_agent import RetrievalAgent

from pathlib import Path

KB_PATH = Path(__file__).resolve().parent.parent / "knowledge_base" / "it_support_kb.md"

class Orchestrator:

    def __init__(self):

        #LLM
        self.llm = AzureChatLLM()
        llm = self.llm

        # DATA (Databricks)
        self.databricks_connector = DatabricksConnector()
        try:
            self.data = self.databricks_connector.load_data()
        except Exception:
            self.data = []

        #  Retrieval Agent (RAG)
        try:
            retriever = RetrievalAgent()
        except Exception:
            retriever = None

        # Agents
        self.l0 = L0Agent(llm, kb_path=KB_PATH)
        self.l1 = L1Agent(llm, retriever=retriever)

        self.fraud = FraudAgent(llm)
        self.sentiment = SentimentAgent(llm)
        self.compliance = ComplianceAgent(llm)
        self.privacy = PrivacyAgent()

        # Optional providers sourced from L0 when available.
        self.azure_kb = getattr(self.l0, "kb", None)
        self.memory = getattr(self.l0, "memory", None)
        self.user_agent = None

    def _detect_user_language(self, query: str) -> str:
        """Return a best-effort ISO 639-1 language code for the user query."""
        text = str(query or "").strip()
        if not text:
            return "en"

        try:
            detection_prompt = f"""
Detect the primary language of the text below.
Return ONLY a 2-letter ISO 639-1 code in lowercase (examples: en, fr, es, de, ar, it, pt, nl, zh, ja, ko, ru).
If uncertain, return en.

Text:
{text}
"""
            raw = self.llm(detection_prompt).strip().lower()
            match = re.search(r"\b([a-z]{2})\b", raw)
            if match:
                return match.group(1)
        except Exception:
            pass

        return "en"

    def handle_user_query(self, query):
        privacy_result = self.privacy.process(query, language="fr")
        query_safe = privacy_result.get("anonymized_text", str(query or ""))
        user_language = self._detect_user_language(query_safe)

        # -------------------------------
        # 1. USER CONTEXT
        # -------------------------------
        user_context = ""
        if self.user_agent and hasattr(self.user_agent, "get_user_context"):
            user_context = self.user_agent.get_user_context(query_safe)

        # -------------------------------
        # 2. FRAUD CHECK
        # -------------------------------
        fraud_result = self.fraud.analyze(query_safe)

        if fraud_result.get("is_fraud", False):
            return {
                "response": "🚨 Activité suspecte détectée. Veuillez contacter le support.",
                "escalated": False,
                "escalation_reason": "fraud_detected",
                "agent": "blocked",
                "sentiment": "neutre",
                "language": user_language,
            }

        # -------------------------------
        # 3. SENTIMENT
        # -------------------------------
        sentiment = self.sentiment.analyze(query_safe)
        tone_hint = sentiment.get("tone_hint", "neutre")

        # -------------------------------
        # 4. DATA (DATABRICKS)
        # -------------------------------
        db_data = []
        try:
            db_data = self.databricks_connector.load_data()
        except Exception:
            db_data = self.data if isinstance(self.data, list) else []

        db_context = "\n".join([
            d.get("text", "") if isinstance(d, dict) else str(d)
            for d in db_data
        ])

        # -------------------------------
        # 5. KB (AZURE)
        # -------------------------------
        kb_results = []
        if self.azure_kb and hasattr(self.azure_kb, "search"):
            kb_results = self.azure_kb.search(query_safe)

        kb_context = "\n".join([
            r.get("text", "") if isinstance(r, dict) else str(r)
            for r in kb_results
        ])

        # -------------------------------
        # 6. MEMORY
        # -------------------------------
        memory_context = ""
        if self.memory and hasattr(self.memory, "search"):
            memory_hits = self.memory.search(query_safe)
            # Avoid language drift: pass only lightweight metadata, not full past responses.
            compact_hits = []
            for hit in memory_hits or []:
                if isinstance(hit, dict):
                    compact_hits.append({
                        "query": hit.get("query", ""),
                        "decision": hit.get("decision", ""),
                    })
                else:
                    compact_hits.append({"query": str(hit), "decision": ""})
            memory_context = json.dumps(compact_hits, ensure_ascii=False)

        # -------------------------------
        # 7. CONTEXTE GLOBAL
        # -------------------------------
        full_context = f"""
    User: {user_context}

    Query: {query_safe}

    Knowledge Base:
    {kb_context}

    Data:
    {db_context}

    Memory:
    {memory_context}
    """

        # -------------------------------
        # 8. L0
        # -------------------------------
        try:
            l0_result = self.l0.handle(
                query_safe,
                tone_hint=tone_hint,
                context=full_context,
                user_language=user_language,
            )
        except Exception:
            l0_result = {
                "decision": "answer",
                "response": "Je rencontre une indisponibilité temporaire. Merci de réessayer dans quelques instants.",
            }

        # -------------------------------
        # 9. L1 SI BESOIN
        # -------------------------------
        escalated = l0_result.get("decision") == "escalate"
        escalation_reason = l0_result.get("escalation_reason") if escalated else None

        if escalated:
            try:
                l1_result = self.l1.diagnose_from_escalation(
                    {
                        "user_query": query_safe,
                        "full_context": full_context,
                        "user_language": user_language,
                    }
                )
                raw_response = l1_result.get("technical_analysis", "")
            except Exception:
                raw_response = "Un expert va analyser votre problème."
        else:
            raw_response = l0_result.get("response", "")

        # -------------------------------
        # 10.  HUMANISATION (CRITIQUE)
        # -------------------------------
        if escalated:
            humanization_prompt = f"""
    You are an expert L1 banking advisor.
    Start your reply with a short professional introduction adapted to the user's language.
    Then deliver the answer in a human and empathetic way.

    CRITICAL: You MUST reply in the EXACT same language as the user's original question.
    Target language code: {user_language}
    Do NOT translate or switch language under any circumstances.
    User's original question: {query_safe}

    Client sentiment: {sentiment.get('sentiment')}
    Expected tone: {tone_hint}

    Technical response to humanize:
    {raw_response}
    """
        else:
            humanization_prompt = f"""
    You are a professional banking assistant.

    CRITICAL: You MUST reply in the EXACT same language as the user's original question.
    Target language code: {user_language}
    Do NOT translate or switch language under any circumstances.
    User's original question: {query_safe}

    Client sentiment: {sentiment.get('sentiment')}
    Tone: {tone_hint}

    Technical response to humanize:
    {raw_response}
    """

        final_response = self.llm(humanization_prompt)

        # -------------------------------
        # 11. COMPLIANCE + RETURN
        # -------------------------------
        try:
            compliance = self.compliance.check(final_response, query_safe, user_language=user_language)
            # Only apply compliance rewrite when the answer is not compliant.
            # This preserves the language chosen in the humanization step.
            if compliance and not compliance.get("is_compliant", True):
                final_response = compliance.get("corrected_response", final_response)
        except Exception:
            compliance = None

        # -------------------------------
        # 12. LANGUAGE LOCK (FINAL GUARD)
        # -------------------------------
        try:
            language_lock_prompt = f"""
You are a strict language guard.

User original question:
{query_safe}

Assistant response draft:
{final_response}

Task:
- Return the response in the EXACT same language as the user's original question.
- Target language code is: {user_language}
- Keep the same meaning, level of detail, and professional tone.
- Do not add explanations about translation.
- Output only the final response text.
"""
            final_response = self.llm(language_lock_prompt)
        except Exception:
            pass

        return {
            "response": final_response,
            "escalated": escalated,
            "escalation_reason": escalation_reason,
            "agent": "L1" if escalated else "L0",
            "sentiment": sentiment.get("sentiment", "neutre"),
            "compliance": compliance,
            "language": user_language,
            "privacy": {
                "anonymized_query": query_safe,
                "detected_entities": privacy_result.get("detected_entities", []),
            },
        }