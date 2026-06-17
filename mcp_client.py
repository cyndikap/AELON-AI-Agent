# mcp_client.py

from dotenv import load_dotenv
load_dotenv()
import os
import requests
from typing import Optional, Dict, Any


class MCPClient:
    """
    MCPClient:
    - Low-level HTTP client for the MCP Server
    - Handles authentication, headers, and error handling
    - Used ONLY by MCPClientAgent (never directly by reasoning agents)
    """

    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.token = os.getenv("MCP_TOKEN")

        if not self.token:
            raise RuntimeError("Environment variable MCP_TOKEN is not set.")

        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    # --------------------------------------------------
    # Core HTTP helpers
    # --------------------------------------------------
    def _get(self, endpoint: str) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        response = requests.get(url, headers=self.headers)

        self._handle_errors(response)
        return response.json()

    def _post(self, endpoint: str, json: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        response = requests.post(url, headers=self.headers, json=json)

        self._handle_errors(response)
        return response.json()

    def _handle_errors(self, response: requests.Response):
        if response.status_code == 401:
            raise PermissionError("Unauthorized MCP request")
        if response.status_code >= 400:
            raise RuntimeError(
                f"MCP request failed [{response.status_code}]: {response.text}"
            )

    # --------------------------------------------------
    # LOG ENDPOINTS
    # --------------------------------------------------
    def get_all_logs(
        self,
        service: Optional[str] = None,
        severity: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        GET /logs
        Optional query params: service, severity
        """
        params = []
        if service:
            params.append(f"service={service}")
        if severity:
            params.append(f"severity={severity}")

        query = "?" + "&".join(params) if params else ""
        return self._get(f"/logs{query}")

    def get_log_by_id(self, log_id: int) -> Dict[str, Any]:
        """
        GET /logs/{id}
        """
        return self._get(f"/logs/{log_id}")

    def create_log(self, service: str, severity: str, message: str) -> Dict[str, Any]:
        """
        POST /logs
        """
        payload = {
            "service": service,
            "severity": severity,
            "message": message
        }
        return self._post("/logs", json=payload)

    # --------------------------------------------------
    # INCIDENT ENDPOINTS
    # --------------------------------------------------
    def create_incident(
        self,
        category: str,
        description: str,
        customer_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        POST /incidents
        """
        payload = {
            "category": category,
            "description": description,
            "customer_id": customer_id
        }
        return self._post("/incidents", json=payload)

    def get_incidents(self) -> Dict[str, Any]:
        """
        GET /incidents (if implemented in MCP server)
        """
        return self._get("/incidents")