# multi_agent/mcp_client_agent.py

from typing import Optional, Dict, Any, List
from mcp_client import MCPClient


class MCPClientAgent:
    """
    MCP Client Agent:
    - Thin tool wrapper over MCPClient
    - No reasoning
    - No business logic
    - Used by L1 / L2 / Fraud agents
    """

    def __init__(self):
        self.client = MCPClient()

    # --------------------------------------------------
    # LOG QUERIES
    # --------------------------------------------------
    def fetch_logs(
        self,
        service: Optional[str] = None,
        severity: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Fetch logs from MCP server.
        """
        return self.client.get_all_logs(
            service=service,
            severity=severity
        )

    def fetch_log_by_id(self, log_id: int) -> Dict[str, Any]:
        """
        Fetch a single log entry by ID.
        """
        return self.client.get_log_by_id(log_id)

    def create_log(
        self,
        service: str,
        severity: str,
        message: str
    ) -> Dict[str, Any]:
        """
        Submit a new log to MCP server.
        """
        payload = {
            "service": service,
            "severity": severity,
            "message": message
        }
        return self.client.post("/logs", json=payload)

    # --------------------------------------------------
    # INCIDENT QUERIES
    # --------------------------------------------------
    def create_incident(
        self,
        category: str,
        description: str,
        customer_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new incident in MCP server.
        """
        payload = {
            "category": category,
            "description": description,
            "customer_id": customer_id
        }
        return self.client.post("/incidents", json=payload)

    def fetch_incidents(self) -> List[Dict[str, Any]]:
        """
        Retrieve all incidents.
        """
        return self.client.get("/incidents")

