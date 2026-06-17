# ============================================================================
# L1 Agent - First-Level Technical Support Agent
# ============================================================================
# This module implements an L1 (Level 1) technical support agent that:
# - Analyzes user queries about system issues
# - Retrieves relevant historical logs via MCP (Model Context Protocol)
# - Uses RAG (Retrieval-Augmented Generation) for semantic search
# - Provides explainable recommendations using an LLM
#
# The agent combines:
#   1. MCP: Fetches logs from external systems
#   2. RAG: Searches for similar historical incidents
#   3. LLM: Reasons about the issue and generates recommendations
# ============================================================================

from typing import Dict, Any
from multi_agent.mcp_client_agent import MCPClientAgent
from rag_layer import LogRAG


class L1Agent:
    """
    L1 Agent:
    - First-level technical support agent
    - Uses MCP + RAG to analyze issues
    - Produces explainable recommendations
    """

    def __init__(self, llm_callable):
        """
        Initialize the L1 Agent with its core components.
        
        Args:
            llm_callable: A function that takes a string prompt and returns a string response.
                         Can be any LLM backend: OpenAI, Azure OpenAI, HuggingFace, mock, etc.
        
        Attributes:
            self.llm: The LLM callable used for reasoning about issues
            self.mcp_agent: MCP client to fetch logs from remote systems
            self.rag: RAG (Retrieval-Augmented Generation) layer for semantic search
        """
        self.llm = llm_callable
        self.mcp_agent = MCPClientAgent()
        self.rag = LogRAG()

    # ========================================================================
    # Public Entry Point - Main Method Called by Other Agents
    # ========================================================================
    def diagnose(self, user_query: str) -> Dict[str, Any]:
        """
        Main diagnosis method - orchestrates the entire support workflow.
        
        This method executes a 4-step pipeline:
            1. Fetch logs from MCP (remote systems)
            2. Build/refresh the RAG vector store index
            3. Search for similar historical incidents
            4. Use reasoning to generate a recommendation
        
        Args:
            user_query: The user's support request or issue description
        
        Returns:
            A dictionary containing:
            {
                "summary": Brief explanation of the issue,
                "recommendation": Suggested action(s) for the user,
                "confidence": Confidence score (0-1),
                "related_logs": List of related log IDs from history
            }
        """
        # Step 1 - Retrieve logs via MCP
        logs = self._get_logs()

        # Step 2 - Build / refresh RAG index
        self._build_rag_index(logs)

        # STEP 3 — Refresh RAG incrementally (faster than full rebuild)
        self.rag.incremental_refresh()

        # Step 4 - Retrieve similar events
        similar_logs = self._retrieve_similar_logs(user_query)

        # Step 4 - Reason and build structured response
        analysis = self._reason(user_query, similar_logs)

        return analysis

    # ========================================================================
    # Internal Pipeline Steps - Helper Methods for the Diagnosis Workflow
    # ========================================================================
    def _get_logs(self):
        """
        Step 1: Retrieve system logs via MCP (Model Context Protocol).
        
        MCP acts as a bridge to external log sources. This method fetches
        all available logs that will be indexed in the RAG system.
        
        Returns:
            A list of log objects, each containing service, severity, message, etc.
        """
        response = self.mcp_agent.fetch_logs()
        return response.get("logs", [])

    def _build_rag_index(self, logs):
        """
        Step 2: Build or refresh the RAG vector store index.
        
        RAG (Retrieval-Augmented Generation) converts logs into vector embeddings
        so that we can perform semantic search. The LLM never directly processes
        all logs - instead, we retrieve only the most relevant ones.
        
        This method is idempotent - can be called multiple times without issues.
        
        Args:
            logs: List of log objects to index
        """
        if not logs:
            return
        self.rag.build_vector_store()

    def _retrieve_similar_logs(self, query: str):
        """
        Step 3: Retrieve semantically similar logs from the RAG index.
        
        This performs semantic search using the query to find the top 3 most
        relevant historical incidents. The search is based on meaning, not keywords.
        
        Args:
            query: The user's issue description
        
        Returns:
            A list of matching log entries ranked by relevance (top_k=3)
        """
        return self.rag.search(query, top_k=3)

    def _reason(self, query: str, matches):
        """
        Step 4: Perform LLM reasoning using retrieved context.
        
        This is the core reasoning step:
        - If no matches found, escalate to human support
        - Otherwise, format retrieved logs as context and feed to LLM
        - The LLM produces a diagnosis and recommendation
        - Tasks for the LLM:
          1. Explain what's likely happening based on historical logs
          2. Provide concrete L1 actions (no escalation unless needed)
          3. Don't speculate beyond what the logs show
        
        The LLM never sees raw logs directly - only controlled, formatted context.
        This ensures explainability and prevents hallucination on missing data.
        
        Args:
            query: The original user issue
            matches: Retrieved similar log entries from RAG search
        
        Returns:
            A structured response dict with summary, recommendation, confidence, and log IDs
        """
        if not matches:
            # No related incidents found - safe fallback
            return {
                "summary": "No related incidents found",
                "recommendation": "Escalate to human support",
                "confidence": 0.3,
                "related_logs": []
            }

        # Format retrieved logs into a human-readable context string
        # This is the "controlled" context we pass to the LLM
        # Each log is summarized to prevent token wastage and hallucination
        context = "\n".join(
            f"- Service: {m['log']['service']}, "
            f"Severity: {m['log']['severity']}, "
            f"Message: {m['log']['message']}"
            for m in matches
        )

        # Craft a prompt that:
        # 1. Defines the LLM's role (L1 support agent)
        # 2. Provides the user's issue
        # 3. Supplies historical context (from RAG)
        # 4. Constrains the LLM to only use provided information
        prompt = f"""
You are an L1 technical support agent.

User issue:
{query}

Relevant historical logs:
{context}

Tasks:
1. Explain what is likely happening
2. Provide a concrete recommendation (L1 actions only)
3. Do NOT speculate beyond the logs

Return the answer in clear, concise language.
"""

        # Call the LLM with the structured prompt
        llm_response = self.llm(prompt)

        # Build structured response with confidence scoring
        # Confidence increases with number of matching historical incidents
        return {
            "summary": self._extract_summary(llm_response),
            "recommendation": self._extract_recommendation(llm_response),
            "confidence": min(0.9, 0.5 + 0.1 * len(matches)),  # 0.5 base + 0.1 per match
            "related_logs": [m["log"]["id"] for m in matches]  # IDs for traceability
        }

    # ========================================================================
    # Output Parsing Utilities - Extract Recommendation from LLM Response
    # ========================================================================
    # NOTE: These methods are simple and can be improved with proper NLP later
    
    def _extract_summary(self, text: str) -> str:
        """
        Extract the first 300 characters of the LLM response as a summary.
        
        This is a simple heuristic - in production, use NLP extraction.
        
        Args:
            text: Full LLM response text
        
        Returns:
            First line (max 300 chars) for a quick summary
        """
        return text.split("\n")[0][:300]

    def _extract_recommendation(self, text: str) -> str:
        """
        Extract the last 300 characters of the LLM response as the recommendation.
        
        This is a simple heuristic - the assumption is that recommendations come
        later in the LLM's structured response. In production, use proper parsing.
        
        Args:
            text: Full LLM response text
        
        Returns:
            Last 300 chars (typically the concrete recommendation)
        """
        return text[-300:]


    # ========================================================================
    # NOTE: DUPLICATE/INCOMPLETE CODE BELOW - APPEARS TO BE WORK IN PROGRESS
    # ========================================================================
    # This second diagnose method overwrites the first one above.
    # It looks like a refactored version but was not completed or integrated.
    # Decision needed:
    #   - Option 1: Delete this and keep the primary diagnose() method above
    #   - Option 2: Merge incremental_refresh() into the primary workflow
    #   - Option 3: Make this an alternative method with a different name
    
    def diagnose(self, user_query: str):
        """
        ALTERNATIVE WORKFLOW (currently overwrites the main diagnose method above).
        
        This appears to be a revised version that:
        1. Uses incremental_refresh() instead of fetching all logs fresh
        2. Performs semantic search
        3. Calls _reason()
        
        Optimization: This may be more efficient for incremental updates rather
        than rebuilding the entire RAG index each time.
        """
        # STEP 1 — Refresh RAG incrementally (faster than full rebuild)
        self.rag.incremental_refresh()

        # STEP 2 — Semantic search on the vector index
        similar_logs = self.rag.search(user_query)

        # STEP 3 — Reasoning (same as main workflow)
        return self._reason(user_query, similar_logs)