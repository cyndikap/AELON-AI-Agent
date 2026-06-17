#L’orchestrateur joue un rôle central dans le système en coordonnant les différents agents 
# et en orchestrant le flux de traitement des requêtes clients, 
# #depuis leur analyse jusqu’à la génération de la réponse finale.



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
        self.data = self.databricks_connector.load_data()

        #  Retrieval Agent (RAG)
        retriever = RetrievalAgent()

        # Agents
        self.l0 = L0Agent(llm, kb_path=KB_PATH)
        self.l1 = L1Agent(llm, retriever=retriever)

        self.fraud = FraudAgent(llm)
        self.sentiment = SentimentAgent(llm)
        self.compliance = ComplianceAgent(llm)

    def handle_user_query(self, query):

        # -------------------------------
        # 1. USER CONTEXT
        # -------------------------------
        user_context = ""
        try:
            user_context = self.user_agent.get_user_context(query)
        except:
            pass

        # -------------------------------
        # 2. FRAUD CHECK
        # -------------------------------
        fraud_result = self.fraud.analyze(query)

        if fraud_result.get("is_fraud", False):
            return "🚨 Activité suspecte détectée. Veuillez contacter le support."

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
            db_data = self.db_connector.load_data()
        except:
            pass

        db_context = "\n".join([d.get("text", "") for d in db_data])

        # -------------------------------
        # 5. KB (AZURE)
        # -------------------------------
        kb_results = []
        try:
            kb_results = self.azure_kb.search(query)
        except:
            pass

        kb_context = "\n".join([r.get("text", "") for r in kb_results])

        # -------------------------------
        # 6. MEMORY
        # -------------------------------
        memory_context = ""
        try:
            memory_context = self.memory.search(query)
        except:
            pass

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
        l0_result = self.l0.handle(
            full_context,
            tone_hint=tone_hint
        )

        # -------------------------------
        # 9. L1 SI BESOIN
        # -------------------------------
        if l0_result.get("decision") == "escalate":
            try:
                l1_result = self.l1.diagnose_from_escalation(full_context)
                raw_response = l1_result.get("technical_analysis", "")
            except:
                raw_response = "Un expert va analyser votre problème."
        else:
            raw_response = l0_result.get("response", "")

        # -------------------------------
        # 10.  HUMANISATION (CRITIQUE)
        # -------------------------------
        final_response = self.llm(
            f"""
    Tu es un assistant bancaire professionnel.

    Client: {sentiment.get('sentiment')}
    Ton: {tone_hint}

    Réponse technique:
    {raw_response}

    Transforme cette réponse en message humain, empathique et clair.
    """
        )

        # -------------------------------
        # 11. COMPLIANCE
        # -------------------------------
        try:
            compliance = self.compliance.check(final_response, query)
            return compliance.get("corrected_response", final_response)
        except:
            return final_response