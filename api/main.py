from dotenv import load_dotenv
load_dotenv()

import json, os
from fastapi import FastAPI, Depends, HTTPException
from api.schemas import UserQueryRequest, AgentResponse, IncidentRequest
from multi_agent.orchestrator import Orchestrator
from multi_agent.privacy.privacy_agent import PrivacyAgent
from auth import authenticate
from models import LogEntry, QueryResponse, NewLogRequest, Incident as IncidentModel
from typing import List, Optional
from datetime import datetime

app = FastAPI(title="Agentic Support API", version="0.2.0")
orchestrator = Orchestrator()
privacy_agent = PrivacyAgent()

LOGS_PATH = "data/processed/logs_clean.json"
mock_incidents: list = []

def _load_logs() -> List[LogEntry]:
    if not os.path.exists(LOGS_PATH):
        return []
    with open(LOGS_PATH, encoding="utf-8") as f:
        raw = json.load(f)
    return [
        LogEntry(
            id=int(r["id"]),
            timestamp=r["timestamp"],
            service=r["service"],
            severity=r["severity"],
            message=r["message"],
        )
        for r in raw
    ]

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/logs", response_model=QueryResponse, dependencies=[Depends(authenticate)])
def get_logs(service: Optional[str] = None, severity: Optional[str] = None):
    logs = _load_logs()
    if service:
        logs = [l for l in logs if l.service == service]
    if severity:
        logs = [l for l in logs if l.severity == severity]
    return QueryResponse(logs=logs, count=len(logs))

@app.get("/logs/{log_id}", response_model=LogEntry, dependencies=[Depends(authenticate)])
def get_log_by_id(log_id: int):
    for log in _load_logs():
        if log.id == log_id:
            return log
    raise HTTPException(status_code=404, detail="Log not found")

@app.post("/logs", response_model=LogEntry, dependencies=[Depends(authenticate)])
def create_log(payload: NewLogRequest):
    logs = _load_logs()
    new_id = max(l.id for l in logs) + 1 if logs else 1

    message_privacy = privacy_agent.process(payload.message, language="fr")
    safe_message = message_privacy.get("anonymized_text", payload.message)

    new_log = LogEntry(
        id=new_id,
        timestamp=datetime.utcnow().isoformat(),
        service=payload.service,
        severity=payload.severity,
        message=safe_message,
    )
    # Persist back
    raw = json.loads(open(LOGS_PATH, encoding="utf-8").read()) if os.path.exists(LOGS_PATH) else []
    raw.append(new_log.model_dump())
    with open(LOGS_PATH, "w", encoding="utf-8") as f:
        json.dump(raw, f, ensure_ascii=False, indent=2)
    return new_log

@app.get("/incidents", dependencies=[Depends(authenticate)])
def get_incidents():
    return mock_incidents

@app.post("/incidents", dependencies=[Depends(authenticate)])
def create_incident_endpoint(payload: IncidentRequest):
    new_incident = IncidentModel(
        id=len(mock_incidents) + 1,
        category=payload.category,
        description=payload.description,
        customer_id=payload.customer_id,
        status="open",
    )
    mock_incidents.append(new_incident)
    return new_incident

@app.post("/support/query", response_model=AgentResponse, dependencies=[Depends(authenticate)])
def handle_query(payload: UserQueryRequest):
    privacy_result = privacy_agent.process(payload.query, language="fr")
    safe_query = privacy_result.get("anonymized_text", payload.query)

    response = orchestrator.handle_user_query(safe_query)
    if not isinstance(response, dict):
        response = {
            "response": str(response),
            "escalated": False,
            "escalation_reason": None,
            "agent": "unknown",
            "sentiment": None,
        }

    return AgentResponse(
        response=response.get("response", ""),
        escalated=bool(response.get("escalated", False)),
        escalation_reason=response.get("escalation_reason"),
        agent=response.get("agent", "unknown"),
        sentiment=response.get("sentiment"),
    )

@app.get("/analytics", dependencies=[Depends(authenticate)])
def get_analytics():
    return orchestrator.get_analytics() if hasattr(orchestrator, "get_analytics") else {}
