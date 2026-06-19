#L’orchestrateur joue un rôle central dans le système en coordonnant les différents agents 
# et en orchestrant le flux de traitement des requêtes clients, 
# #depuis leur analyse jusqu’à la génération de la réponse finale.



import json
from dotenv import load_dotenv
load_dotenv()

from azure_chat_llm import AzureChatLLM
from multi_agent.l0.l0_agent import L0Agent
from multi_agent.l1.l1_agent import L1Agent
from multi_agent.fraud.fraud_agent import FraudAgent
from multi_agent.sentiment.sentiment_agent import SentimentAgent
from multi_agent.compliance.compliance_agent import ComplianceAgent

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

        # Optional providers sourced from L0 when available.
        self.azure_kb = getattr(self.l0, "kb", None)
        self.memory = getattr(self.l0, "memory", None)
        self.user_agent = None

    def handle_user_query(self, query):

        # -------------------------------
        # 1. USER CONTEXT
        # -------------------------------
        user_context = ""
        if self.user_agent and hasattr(self.user_agent, "get_user_context"):
            user_context = self.user_agent.get_user_context(query)

        # -------------------------------
        # 2. FRAUD CHECK
        # -------------------------------
        fraud_result = self.fraud.analyze(query)

        if fraud_result.get("is_fraud", False):
            return {
                "response": "🚨 Activité suspecte détectée. Veuillez contacter le support.",
                "escalated": False,
                "escalation_reason": "fraud_detected",
                "agent": "blocked",
                "sentiment": "neutre",
            }

        # -------------------------------
        # 3. SENTIMENT
        # -------------------------------
        sentiment = self.sentiment.analyze(query)
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
            kb_results = self.azure_kb.search(query)

        kb_context = "\n".join([
            r.get("text", "") if isinstance(r, dict) else str(r)
            for r in kb_results
        ])

        # -------------------------------
        # 6. MEMORY
        # -------------------------------
        memory_context = ""
        if self.memory and hasattr(self.memory, "search"):
            memory_hits = self.memory.search(query)
            memory_context = json.dumps(memory_hits, ensure_ascii=False)

        # -------------------------------
        # 7. CONTEXTE GLOBAL
        # -------------------------------
        full_context = f"""
    User: {user_context}

    Query: {query}

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
                full_context,
                tone_hint=tone_hint
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
                    {"user_query": query, "full_context": full_context}
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
    Tu es un conseiller bancaire expert (niveau L1).
    Commence ta réponse par une présentation : "Bonjour, je suis votre conseiller spécialisé. Je prends en charge votre demande."
    Puis donne la réponse de manière humaine et empathique.

    Sentiment client: {sentiment.get('sentiment')}
    Ton attendu: {tone_hint}

    Réponse technique:
    {raw_response}

    Transforme cette réponse en message humain, empathique et clair.
    """
        else:
            humanization_prompt = f"""
    Tu es un assistant bancaire professionnel.

    Client: {sentiment.get('sentiment')}
    Ton: {tone_hint}

    Réponse technique:
    {raw_response}

    Transforme cette réponse en message humain, empathique et clair.
    """

        final_response = self.llm(humanization_prompt)

        # -------------------------------
        # 11. COMPLIANCE + RETURN
        # -------------------------------
        try:
            compliance = self.compliance.check(final_response, query)
            final_response = compliance.get("corrected_response", final_response)
        except Exception:
            compliance = None

        return {
            "response": final_response,
            "escalated": escalated,
            "escalation_reason": escalation_reason,
            "agent": "L1" if escalated else "L0",
            "sentiment": sentiment.get("sentiment", "neutre"),
            "compliance": compliance,
        }