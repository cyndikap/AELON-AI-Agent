from pydantic import BaseModel
from typing import Optional, Any

class UserQueryRequest(BaseModel):
    query: str

class AgentResponse(BaseModel):
    response: str
    escalated: bool = False
    escalation_reason: Optional[str] = None
    agent: str = "unknown"
    sentiment: Optional[Any] = None

class IncidentRequest(BaseModel):
    category: str
    description: str
    customer_id: Optional[str] = None
