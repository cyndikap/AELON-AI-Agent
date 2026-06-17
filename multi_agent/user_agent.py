from typing import Dict, Any

class UserAgent:
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator

    def handle(self, query: str) -> Dict[str, Any]:
        return self.orchestrator.handle_user_query(query)
