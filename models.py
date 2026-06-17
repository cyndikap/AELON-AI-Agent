from pydantic import BaseModel
from typing import List, Optional

class NewLogRequest(BaseModel):
    service: str
    severity: str
    message: str

class Incident(BaseModel):
    id: int
    category: str
    description: str
    customer_id: Optional[str] = None
    status: str = "open"  # open, investigating, resolved

class NewIncidentRequest(BaseModel):
    category: str
    description: str
    customer_id: Optional[str] = None


# --------------------------
# Log models
# --------------------------
class LogEntry(BaseModel):
    id: int
    timestamp: str
    service: str
    severity: str
    message: str

class QueryResponse(BaseModel):
    logs: List[LogEntry]
    count: int

class NewLogRequest(BaseModel):
    service: str
    severity: str
    message: str

# --------------------------
# Incident models
# --------------------------
class Incident(BaseModel):
    id: int
    category: str
    description: str
    customer_id: Optional[str] = None
    status: str = "open"

