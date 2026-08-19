#L’orchestrateur joue un rôle central dans le système en coordonnant les différents agents 
# et en orchestrant le flux de traitement des requêtes clients, 
# #depuis leur analyse jusqu’à la génération de la réponse finale.



import json
import logging
import re
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
load_dotenv()

from azure_chat_llm import AzureChatLLM
from multi_agent.l0.l0_agent import L0Agent
from multi_agent.l1.l1_agent import L1Agent
from multi_agent.fraud.fraud_agent import FraudAgent
from multi_agent.sentiment.sentiment_agent import SentimentAgent
from multi_agent.compliance.compliance_agent import ComplianceAgent
from multi_agent.privacy.privacy_agent import PrivacyAgent
from multi_agent.evaluation.evaluation_agent import EvaluationAgent
from multi_agent.explainability.explainability_agent import ExplainabilityAgent
from multi_agent.observability.observability_agent import ObservabilityAgent
from multi_agent.analytics.analytics_agent import AnalyticsAgent
from multi_agent.conversation_logger import ConversationLogger, ConversationRecord
from multi_agent.retrieval.retrieval_agent import retrieve_context
from multi_agent.data_access.databricks_connector import DatabricksConnector
from multi_agent.retrieval.retrieval_agent import RetrievalAgent

KB_PATH = Path(__file__).resolve().parent.parent / "knowledge_base" / "it_support_kb.md"

logger = logging.getLogger("aelon.orchestrator")


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
        self.evaluation = EvaluationAgent()
        self.explainability = ExplainabilityAgent()
        self.observability = ObservabilityAgent()
        self.analytics = AnalyticsAgent()
        self.conversation_logger = ConversationLogger()

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
            logger.info("llm.start stage=language_detection")
            raw = self.llm(detection_prompt).strip().lower()
            logger.info("llm.end stage=language_detection")
            match = re.search(r"\b([a-z]{2})\b", raw)
            if match:
                return match.group(1)
        except Exception:
            pass

        return "en"

    def handle_user_query(self, query, user_session_id="anonymous"):
        request_started = time.perf_counter()
        logger.info("orchestrator.start")
        logger.info("orchestrator.handle_user_query start query=%s", query)
        privacy_result = self.privacy.process(query, language="fr")
        query_safe = privacy_result.get("anonymized_text", str(query or ""))
        question = query_safe
        user_language = self._detect_user_language(query_safe)
        logger.info("orchestrator.language=%s safe_query=%s", user_language, query_safe)

        def _persist_conversation(answer: str, sources_payload: list[dict], retrieval_count: int) -> None:
            response_time_ms = round((time.perf_counter() - request_started) * 1000, 2)
            sources = [item.get("source", "") for item in sources_payload if isinstance(item, dict) and item.get("source")]
            categories = [item.get("categorie", "") for item in sources_payload if isinstance(item, dict) and item.get("categorie")]

            save_result = self.conversation_logger.save(
                ConversationRecord(
                    question=question,
                    answer=answer,
                    sources=sources,
                    categories=categories,
                    retrieval_count=retrieval_count,
                    response_time_ms=response_time_ms,
                    user_session_id=user_session_id,
                )
            )
            if save_result.get("saved"):
                logger.info("conversation.saved conversation_id=%s", save_result.get("conversation_id"))
            else:
                logger.warning("conversation.saved.failed reason=%s", save_result.get("reason"))

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
        logger.info("orchestrator.fraud_result=%s", fraud_result)

        if fraud_result.get("is_fraud", False):
            blocked_response = "🚨 Activité suspecte détectée. Veuillez contacter le support."
            evaluation = self.evaluation.evaluate(
                question=query_safe,
                answer=blocked_response,
                retrieved_docs=[],
            )
            _persist_conversation(answer=blocked_response, sources_payload=[], retrieval_count=0)
            logger.info("orchestrator.end")
            return {
                "answer": blocked_response,
                "response": blocked_response,
                "evaluation": evaluation,
                "escalated": False,
                "escalation_reason": "fraud_detected",
                "agent": "blocked",
                "sentiment": "neutre",
                "language": user_language,
                "response_time_ms": round((time.perf_counter() - request_started) * 1000, 2),
            }

        # -------------------------------
        # 3. SENTIMENT
        # -------------------------------
        sentiment = self.sentiment.analyze(query_safe)
        tone_hint = sentiment.get("tone_hint", "neutre")
        logger.info("orchestrator.sentiment=%s tone_hint=%s", sentiment, tone_hint)

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
        # 4.1 RETRIEVAL CONTEXT
        # -------------------------------
        retrieval_results = {"result": {"data_array": []}}
        try:
            retrieval_results = retrieve_context(question)
        except Exception:
            logger.exception("orchestrator.retrieval.failed")

        retrieval_rows = retrieval_results.get("result", {}).get("data_array", [])
        retrieval_context = ""
        for row in retrieval_rows:
            if len(row) > 1:
                retrieval_context += f"{row[1]}\n\n"

        retrieval_sources = []
        for row in retrieval_rows:
            retrieval_sources.append({
                "source": row[2] if len(row) > 2 else "",
                "categorie": row[3] if len(row) > 3 else "",
            })

        # -------------------------------
        # 5. KB (AZURE)
        # -------------------------------
        kb_results = []
        if self.azure_kb and hasattr(self.azure_kb, "search"):
            kb_results = self.azure_kb.search(query_safe)

        retrieved_docs = [
            r.get("text", "") if isinstance(r, dict) else str(r)
            for r in kb_results
        ]

        kb_context = "\n".join([
            r.get("text", "") if isinstance(r, dict) else str(r)
            for r in kb_results
        ])

        if retrieval_context.strip():
            retrieved_docs.extend([
                row[1]
                for row in retrieval_rows
                if len(row) > 1 and str(row[1]).strip()
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

    Retrieved context:
    {retrieval_context}

    Memory:
    {memory_context}
    """

        rag_prompt = f"""
Contexte documentaire :

{retrieval_context}

Question utilisateur :

{question}

Reponds a partir des documents fournis.
"""
        retrieval_answer = ""
        if retrieval_context.strip():
            try:
                logger.info("llm.start stage=retrieval_answer")
                retrieval_answer = self.llm(rag_prompt)
                logger.info("llm.end stage=retrieval_answer")
            except Exception:
                logger.exception("orchestrator.retrieval_prompt.failed")

        # -------------------------------
        # 8. L0
        # -------------------------------
        try:
            logger.info("orchestrator.l0.start")
            l0_result = self.l0.handle(
                query_safe,
                tone_hint=tone_hint,
                context=full_context,
                user_language=user_language,
            )
            logger.info("orchestrator.l0.result=%s", l0_result)
        except Exception:
            logger.exception("orchestrator.l0.failed")
            l0_result = {
                "decision": "answer",
                "response": "Je rencontre une indisponibilité temporaire. Merci de réessayer dans quelques instants.",
            }

        # -------------------------------
        # 9. L1 SI BESOIN
        # -------------------------------
        escalated = l0_result.get("decision") == "escalate"
        escalation_reason = l0_result.get("escalation_reason") if escalated else None
        l1_result = {}

        if escalated:
            try:
                logger.info("orchestrator.l1.start")
                l1_result = self.l1.diagnose_from_escalation(
                    {
                        "user_query": query_safe,
                        "full_context": full_context,
                        "user_language": user_language,
                    }
                )
                logger.info("orchestrator.l1.result=%s", l1_result)
                raw_response = l1_result.get("technical_analysis", "")
                related_logs = l1_result.get("related_logs", [])
                retrieved_docs.extend([
                    item.get("text", "") if isinstance(item, dict) else str(item)
                    for item in related_logs
                ])
            except Exception:
                raw_response = "Un expert va analyser votre problème."
        else:
            raw_response = retrieval_answer or l0_result.get("response", "")

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

        logger.info("llm.start stage=humanization")
        final_response = self.llm(humanization_prompt)
        logger.info("llm.end stage=humanization")

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
            logger.info("llm.start stage=language_lock")
            final_response = self.llm(language_lock_prompt)
            logger.info("llm.end stage=language_lock")
        except Exception:
            pass

        evaluation = self.evaluation.evaluate(
            question=query_safe,
            answer=final_response,
            retrieved_docs=[doc for doc in retrieved_docs if str(doc).strip()],
        )
        logger.info("orchestrator.explainability.start")
        explanation = self.explainability.explain(
            user_query=query_safe,
            response=final_response,
            agent_used="L1" if escalated else "L0",
            escalated=escalated,
            escalation_reason=escalation_reason,
            retrieved_context=retrieved_docs,
            quality_score=evaluation.get("answer_quality", 0.0),
        )
        logger.info("orchestrator.explainability.result=%s", explanation)

        logger.info("orchestrator.observability.start")
        observability = self.observability.analyze(final_response, {
            "escalated_count": 1 if escalated else 0,
            "escalated": escalated,
        })
        logger.info("orchestrator.observability.result=%s", observability)

        logger.info("orchestrator.analytics.start")
        df = pd.DataFrame([{
            "query": query_safe,
            "answer": final_response,
            "agent": "L1" if escalated else "L0",
            "is_fraud": fraud_result.get("is_fraud", False),
            "risk_level": fraud_result.get("risk_level", "low"),
            "category": "support",
            "sentiment": sentiment.get("sentiment", "neutre"),
            "answer_quality": evaluation.get("answer_quality", 0.0),
            "relevance_score": evaluation.get("relevance_score", 0.0),
            "faithfulness_score": evaluation.get("faithfulness_score", 0.0),
            "compliance_score": evaluation.get("compliance_score", 0.0),
            "hallucination_rate": evaluation.get("hallucination_rate", 0.0),
            "timestamp": datetime.utcnow().isoformat(),
        }])
        analytics = self.analytics.compute_metrics(df)
        logger.info("orchestrator.analytics.result=%s", analytics)

        _persist_conversation(
            answer=final_response,
            sources_payload=retrieval_sources,
            retrieval_count=len(retrieval_rows),
        )
        logger.info("orchestrator.end")

        return {
            "answer": final_response,
            "response": final_response,
            "retrieval": retrieval_results,
            "sources": retrieval_sources,
            "evaluation": evaluation,
            "escalated": escalated,
            "escalation_reason": escalation_reason,
            "agent": "L1" if escalated else "L0",
            "sentiment": sentiment.get("sentiment", "neutre"),
            "compliance": compliance,
            "language": user_language,
            "explainability": explanation,
            "observability": observability,
            "analytics": analytics,
            "response_time_ms": round((time.perf_counter() - request_started) * 1000, 2),
            "privacy": {
                "anonymized_query": query_safe,
                "detected_entities": privacy_result.get("detected_entities", []),
            },
        }