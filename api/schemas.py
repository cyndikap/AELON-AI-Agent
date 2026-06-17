from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class UserQueryRequest(BaseModel):
    query: str

class AgentResponse(BaseModel):
    summary: str
    recommendation: str
    confidence: float
    related_logs: List[int]
    agent_used: str
    sentiment: Optional[Dict[str, Any]] = None
    compliance: Optional[Dict[str, Any]] = None

class IncidentRequest(BaseModel):
    category: str
    description: str
    customer_id: Optional[str] = None
