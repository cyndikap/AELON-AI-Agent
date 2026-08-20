from dotenv import load_dotenv
load_dotenv()

import json, os
import logging
from collections import Counter
from statistics import mean
import re
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from api.schemas import UserQueryRequest, AgentResponse, IncidentRequest
from multi_agent.orchestrator import Orchestrator
from multi_agent.privacy.privacy_agent import PrivacyAgent
from auth import authenticate
from models import LogEntry, QueryResponse, NewLogRequest, Incident as IncidentModel
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from utils.category_detector import detect_category
from multi_agent.data_access.databricks_sql_client import DatabricksSQLClient
from multi_agent.evaluation.rag_evaluation_service import RAGEvaluationService

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger("aelon.api")

app = FastAPI(title="Agentic Support API", version="0.2.0")
orchestrator = Orchestrator()
privacy_agent = PrivacyAgent()

WEB_DIR = Path(__file__).resolve().parent.parent / "web"
templates = Jinja2Templates(directory=str(WEB_DIR / "templates"))
if (WEB_DIR / "static").exists():
    app.mount("/static", StaticFiles(directory=str(WEB_DIR / "static")), name="static")
if (WEB_DIR / "css").exists():
    app.mount("/css", StaticFiles(directory=str(WEB_DIR / "css")), name="css")
if (WEB_DIR / "js").exists():
    app.mount("/js", StaticFiles(directory=str(WEB_DIR / "js")), name="js")

LOGS_PATH = "data/processed/logs_clean.json"
WEB_INTERACTIONS_PATH = "data/processed/web_interactions.json"
mock_incidents: list = []
sql_client = DatabricksSQLClient()
ANALYTICS_TABLE = "fr_raise.rag_pipeline.analytics_metrics"
GOVERNANCE_TABLE = "fr_raise.rag_pipeline.governance_metrics"
rag_evaluation_service = RAGEvaluationService(sql_client)


class WebChatRequest(BaseModel):
    query: str


class CopilotQuestionRequest(BaseModel):
    question: str

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


def _ensure_parent(path: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)


def _load_interactions() -> list[dict]:
    if not os.path.exists(WEB_INTERACTIONS_PATH):
        return []
    try:
        with open(WEB_INTERACTIONS_PATH, encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def _save_interactions(rows: list[dict]) -> None:
    _ensure_parent(WEB_INTERACTIONS_PATH)
    with open(WEB_INTERACTIONS_PATH, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)


def _float(value, default=0.0) -> float:
    try:
        return float(value)
    except Exception:
        return float(default)


def _strict_mask_sensitive(text: str) -> str:
    value = str(text or "")
    value = value.replace("[BANK_ACCOUNT]", "[ACCOUNT_NUMBER]")
    value = value.replace("[PHONE]", "[PHONE_NUMBER]")
    # Basic phone masking (FR-like and generic 8-15 contiguous digits with separators).
    value = re.sub(r"\b(?:\+\d{1,3}[\s.-]?)?(?:\d[\s.-]?){8,15}\b", "[PHONE_NUMBER]", value)
    # Account-like long numbers.
    value = re.sub(r"\b\d{9,18}\b", "[ACCOUNT_NUMBER]", value)
    # Bank card full numbers (13-19 digits with optional spaces/dashes).
    value = re.sub(r"\b(?:\d[ -]*?){13,19}\b", "[CARD_NUMBER]", value)
    return value


def _mean(rows: list[dict], key: str, default=0.0) -> float:
    values = [_float(r.get(key, default), default) for r in rows]
    return float(mean(values)) if values else float(default)


def _analytics_summary(rows: list[dict]) -> dict:
    if not rows:
        return {
            "kpis": {
                "volume_conversations": 0,
                "escalades": 0,
                "fraudes": 0,
                "quality_moyenne": 0.0,
            },
            "categories": [],
            "sentiments": [],
            "trends_7d": [],
            "recommendations": [
                "Collecter davantage de conversations pour une analyse fiable.",
            ],
        }

    categories = Counter([str(r.get("category", "autre")) for r in rows])
    sentiments = Counter([str(r.get("sentiment", "neutral")) for r in rows])
    escalades = sum(1 for r in rows if bool(r.get("escalated", False)))
    fraudes = sum(1 for r in rows if bool(r.get("is_fraud", False)))
    quality = _mean(rows, "answer_quality", 0.0)

    by_day = Counter()
    for row in rows:
        raw_ts = str(row.get("timestamp", ""))
        day = raw_ts[:10] if len(raw_ts) >= 10 else "unknown"
        by_day[day] += 1

    trends = [
        {"day": d, "count": c}
        for d, c in sorted(by_day.items())[-7:]
    ]

    recommendations = []
    if escalades / max(len(rows), 1) > 0.25:
        recommendations.append("Le taux d'escalade est élevé: enrichir la base de connaissances L0 sur les cas récurrents.")
    if fraudes > 0:
        recommendations.append("Renforcer la prévention fraude avec messages proactifs et parcours de blocage carte.")
    if quality < 65:
        recommendations.append("La qualité moyenne est faible: revoir prompts L0/L1 et améliorer le contexte RAG.")
    if not recommendations:
        recommendations.append("Les indicateurs sont stables; poursuivre le suivi hebdomadaire et les tests de non-régression.")

    return {
        "kpis": {
            "volume_conversations": len(rows),
            "escalades": escalades,
            "fraudes": fraudes,
            "quality_moyenne": round(quality, 2),
        },
        "categories": [{"label": k, "count": v} for k, v in categories.items()],
        "sentiments": [{"label": k, "count": v} for k, v in sentiments.items()],
        "trends_7d": trends,
        "recommendations": recommendations,
    }


def _governance_summary(rows: list[dict]) -> dict:
    if not rows:
        return {
            "evaluation": {
                "relevance_score": 0.0,
                "faithfulness_score": 0.0,
                "hallucination_rate": 0.0,
                "compliance_score": 0.0,
                "answer_quality": 0.0,
            },
            "observability": {
                "response_time_ms": 0.0,
                "availability": 100.0,
                "quality_score": 0.0,
                "alerts": [],
            },
            "data_quality": {
                "completeness": 0.0,
                "consistency": 0.0,
                "validity": 0.0,
            },
            "lineage": "Chat -> Privacy -> Orchestrator -> Evaluation -> Storage -> Dashboards",
            "compliance": "Contrôles RGPD actifs; masquage des données sensibles avant affichage.",
            "audit": "Traçabilité disponible via historique des conversations et scores d'évaluation.",
            "privacy": "Privacy Agent appliqué avant affichage et persistance.",
            "logs": [],
        }

    required = ["timestamp", "query", "answer", "agent"]
    complete = sum(1 for r in rows if all(str(r.get(k, "")).strip() for k in required))
    consistency = sum(1 for r in rows if str(r.get("agent", "")).strip() in {"L0", "L1", "blocked", "unknown"})
    validity = sum(
        1 for r in rows
        if 0 <= _float(r.get("answer_quality", 0.0)) <= 100
        and 0 <= _float(r.get("relevance_score", 0.0)) <= 100
        and 0 <= _float(r.get("faithfulness_score", 0.0)) <= 100
        and 0 <= _float(r.get("hallucination_rate", 0.0)) <= 100
        and 0 <= _float(r.get("compliance_score", 0.0)) <= 100
    )

    total = max(len(rows), 1)

    evaluation = {
        "relevance_score": round(_mean(rows, "relevance_score", 0.0), 2),
        "faithfulness_score": round(_mean(rows, "faithfulness_score", 0.0), 2),
        "hallucination_rate": round(_mean(rows, "hallucination_rate", 0.0), 2),
        "compliance_score": round(_mean(rows, "compliance_score", 0.0), 2),
        "answer_quality": round(_mean(rows, "answer_quality", 0.0), 2),
    }

    observability = {
        "response_time_ms": round(_mean(rows, "response_time_ms", 0.0), 2),
        "availability": 100.0,
        "quality_score": evaluation["answer_quality"],
        "traces": len(rows),
        "alerts": [],
    }

    if evaluation["answer_quality"] < 60:
        observability["alerts"].append("Quality Score sous le seuil 60.")
    if evaluation["hallucination_rate"] > 35:
        observability["alerts"].append("Hallucination Rate élevé détecté.")
    if observability["response_time_ms"] > 3500:
        observability["alerts"].append("Temps de réponse moyen supérieur à 3.5s.")

    logs = sorted(rows, key=lambda r: str(r.get("timestamp", "")), reverse=True)[:15]

    return {
        "evaluation": evaluation,
        "observability": observability,
        "data_quality": {
            "completeness": round(complete * 100 / total, 2),
            "consistency": round(consistency * 100 / total, 2),
            "validity": round(validity * 100 / total, 2),
        },
        "lineage": "Customer Chat -> Privacy Agent -> Orchestrator (L0/L1/Fraud/Sentiment/Compliance) -> Evaluation Agent -> Storage -> Analytics/Governance Dashboards",
        "compliance": "RGPD/Privacy by design appliqué; données sensibles masquées avant affichage et enregistrement.",
        "audit": "Horodatage, agent, escalade, scores et sentiments conservés pour audit interne.",
        "privacy": "Masquage automatique des numéros de téléphone, comptes, emails et entités sensibles.",
        "logs": logs,
    }


def _safe_query_data_array(statement: str) -> list[list]:
    if not sql_client.is_configured():
        return []
    try:
        return sql_client.query_data_array(statement)
    except Exception:
        return []


def _analytics_kpis() -> dict:
    rows = _safe_query_data_array(
        f"""
SELECT
    total_conversations,
    avg_response_time_ms,
    avg_chunks_retrieved,
    category_counts_json,
    source_counts_json,
    top_queries_json,
    metric_date
FROM {ANALYTICS_TABLE}
ORDER BY metric_date DESC
LIMIT 1
"""
    )
    if rows:
        category_counts = json.loads(rows[0][3] or "{}")
        source_counts = json.loads(rows[0][4] or "{}")
        top_queries = json.loads(rows[0][5] or "[]")
        top_categories = [
            {"category": key, "count": int(value)}
            for key, value in sorted(category_counts.items(), key=lambda item: item[1], reverse=True)[:5]
        ]
        top_sources = [
            {"source": key, "count": int(value)}
            for key, value in sorted(source_counts.items(), key=lambda item: item[1], reverse=True)[:5]
        ]
        return {
            "total_conversations": int(rows[0][0] or 0),
            "avg_response_time_ms": round(float(rows[0][1] or 0.0), 2),
            "avg_chunks_retrieved": round(float(rows[0][2] or 0.0), 2),
            "top_categories": top_categories,
            "top_sources": top_sources,
            "top_queries": top_queries,
            "questions_by_day": [],
            "source": "databricks.analytics_metrics",
        }

    interactions = _load_interactions()
    base = _analytics_summary(interactions)
    return {
        "total_conversations": int(base.get("kpis", {}).get("volume_conversations", 0)),
        "avg_response_time_ms": round(_mean(interactions, "response_time_ms", 0.0), 2),
        "avg_chunks_retrieved": 0.0,
        "top_categories": base.get("categories", []),
        "top_sources": [],
        "top_queries": [],
        "questions_by_day": base.get("trends_7d", []),
        "source": "local.web_interactions",
    }


def _governance_kpis() -> dict:
    rows = _safe_query_data_array(
        f"""
SELECT
    retrieval_success_ratio,
    avg_documents_retrieved,
    retrieval_empty_ratio,
    responses_with_sources,
    responses_without_sources,
    avg_context_chars,
    citations_per_source_json,
    metric_date
FROM {GOVERNANCE_TABLE}
ORDER BY metric_date DESC
LIMIT 1
"""
    )
    if rows:
        citations = json.loads(rows[0][6] or "{}")
        citations_per_source = [
            {"source": key, "count": int(value)}
            for key, value in sorted(citations.items(), key=lambda item: item[1], reverse=True)[:10]
        ]
        retrieval_success_rate = round(float(rows[0][0] or 0.0) * 100.0, 2)
        return {
            "retrieval_success_rate": retrieval_success_rate,
            "avg_documents_retrieved": round(float(rows[0][1] or 0.0), 2),
            "retrieval_empty_rate": round(float(rows[0][2] or 0.0) * 100.0, 2),
            "responses_with_sources": int(rows[0][3] or 0),
            "responses_without_sources": int(rows[0][4] or 0),
            "avg_context_chars": round(float(rows[0][5] or 0.0), 2),
            "citations_per_source": citations_per_source,
            "source": "databricks.governance_metrics",
        }

    interactions = _load_interactions()
    total = max(len(interactions), 1)
    with_sources = sum(1 for row in interactions if row.get("answer"))
    retrieval_success_rate = round((with_sources / total) * 100.0, 2)
    return {
        "retrieval_success_rate": retrieval_success_rate,
        "avg_documents_retrieved": 0.0,
        "retrieval_empty_rate": round(100.0 - retrieval_success_rate, 2),
        "responses_with_sources": with_sources,
        "responses_without_sources": max(total - with_sources, 0),
        "avg_context_chars": round(_mean([{"v": len(str(row.get("answer", "")))} for row in interactions], "v", 0.0), 2),
        "citations_per_source": [],
        "source": "local.web_interactions",
    }


def _evaluation_kpis() -> dict:
    try:
        if sql_client.is_configured():
            summary = rag_evaluation_service.latest_summary()
            details = rag_evaluation_service.latest_details()
            summary["details"] = details
            summary["source"] = "databricks.rag_evaluation"
            return summary
    except Exception:
        pass

    return {
        "total_questions": 0,
        "retrieval_success_rate": 0.0,
        "category_match_rate": 0.0,
        "source_match_rate": 0.0,
        "keyword_match_rate": 0.0,
        "avg_response_time": 0.0,
        "avg_chunks_retrieved": 0.0,
        "category_coverage": 0.0,
        "avg_answer_quality": 0.0,
        "avg_faithfulness_score": 0.0,
        "avg_relevance_score": 0.0,
        "latest_run_at": None,
        "details": [],
        "source": "empty",
    }


def _copilot_answer(question: str, context: dict, mode: str) -> str:
    q = str(question or "").strip()
    if not q:
        return "Merci de poser une question pour lancer l'analyse."

    fallback = ""
    if mode == "analytics":
        fallback = (
            "Lecture rapide des KPI: surveiller le volume, le taux d'escalade, les fraudes et la qualité moyenne. "
            "Si les escalades montent, enrichir la base de connaissance L0 et améliorer la classification des intentions."
        )
    else:
        fallback = (
            "Pour la gouvernance IA: prioriser la baisse du taux d'hallucination, maintenir la compliance au-dessus de 95, "
            "et suivre les alertes de latence et de qualité au quotidien."
        )

    try:
        prompt = f"""
Tu es {"Analytics Copilot" if mode == "analytics" else "AI Governance Copilot"} d'une banque premium.
Réponds en français, de manière professionnelle, concise et actionnable.

Question:
{q}

Contexte KPI/plateforme (JSON):
{json.dumps(context, ensure_ascii=False)}

Contraintes:
- Pas de jargon inutile.
- Donner des recommandations claires en 3 à 6 points.
- Si tendance dégradée, proposer un plan d'action priorisé.
"""
        return str(orchestrator.llm(prompt)).strip()
    except Exception:
        return fallback


@app.get("/", response_class=HTMLResponse)
def web_home(request: Request):
    return RedirectResponse(url="/banking")


@app.get("/banking", response_class=HTMLResponse)
def banking_page(request: Request):
    page_path = WEB_DIR / "pages" / "banking.html"
    if not page_path.exists():
        raise HTTPException(status_code=404, detail="Banking page not found")
    return HTMLResponse(content=page_path.read_text(encoding="utf-8"))


@app.get("/dashboards/analytics", response_class=HTMLResponse)
def analytics_page(request: Request):
    page_path = WEB_DIR / "pages" / "analytics.html"
    if not page_path.exists():
        raise HTTPException(status_code=404, detail="Analytics page not found")
    return HTMLResponse(content=page_path.read_text(encoding="utf-8"))


@app.get("/dashboards/governance", response_class=HTMLResponse)
def governance_page(request: Request):
    page_path = WEB_DIR / "pages" / "governance.html"
    if not page_path.exists():
        raise HTTPException(status_code=404, detail="Governance page not found")
    return HTMLResponse(content=page_path.read_text(encoding="utf-8"))


@app.get("/dashboards/evaluation", response_class=HTMLResponse)
def evaluation_page(request: Request):
    page_path = WEB_DIR / "pages" / "evaluation.html"
    if not page_path.exists():
        raise HTTPException(status_code=404, detail="Evaluation page not found")
    return HTMLResponse(content=page_path.read_text(encoding="utf-8"))


@app.get("/analytics")
def get_analytics_kpis():
    return _analytics_kpis()


@app.get("/governance")
def get_governance_kpis():
    return _governance_kpis()


@app.get("/evaluation")
def get_evaluation_kpis():
    return _evaluation_kpis()


@app.post("/web/chat")
def web_chat(payload: WebChatRequest, request: Request):
    logger.info("web_chat.request start query=%s", payload.query)
    privacy_result = privacy_agent.process(payload.query, language="fr")
    safe_query = _strict_mask_sensitive(privacy_result.get("anonymized_text", payload.query))
    logger.info("web_chat.privacy masked_query=%s", safe_query)

    start = datetime.utcnow()

    session_id = request.headers.get("x-session-id") or request.client.host or "anonymous"
    logger.info("web_chat.orchestrator start session_id=%s", session_id)
    response = orchestrator.handle_user_query(safe_query, user_session_id=session_id)
    logger.info("web_chat.orchestrator result agent=%s escalated=%s", response.get("agent") if isinstance(response, dict) else "unknown", bool(response.get("escalated", False)) if isinstance(response, dict) else False)
    if not isinstance(response, dict):
        response = {
            "answer": str(response),
            "response": str(response),
            "escalated": False,
            "escalation_reason": None,
            "agent": "unknown",
            "sentiment": None,
            "evaluation": {},
        }

    final_answer_raw = response.get("answer") or response.get("response") or ""
    answer_privacy = privacy_agent.process(final_answer_raw, language="fr")
    final_answer = _strict_mask_sensitive(answer_privacy.get("anonymized_text", final_answer_raw))
    evaluation = response.get("evaluation", {}) if isinstance(response.get("evaluation", {}), dict) else {}
    logger.info("web_chat.response ready answer_length=%s agent=%s", len(final_answer), response.get("agent", "unknown"))

    explainability = (
        f"Réponse générée par {response.get('agent', 'L0')}"
        f" | escalade={bool(response.get('escalated', False))}"
        f" | qualité={float(evaluation.get('answer_quality', 0.0)):.1f}/100"
    )

    final_payload = {
        "user_message": safe_query,
        "answer": final_answer,
        "agent": response.get("agent", "unknown"),
        "escalated": bool(response.get("escalated", False)),
        "sentiment": response.get("sentiment"),
        "evaluation": {
            "quality_score": float(evaluation.get("answer_quality", 0.0)),
            "relevance_score": float(evaluation.get("relevance_score", 0.0)),
            "faithfulness_score": float(evaluation.get("faithfulness_score", 0.0)),
            "hallucination_rate": float(evaluation.get("hallucination_rate", 0.0)),
            "compliance_score": float(evaluation.get("compliance_score", 0.0)),
        },
        "explainability": explainability,
        "privacy": {
            "detected_entities": privacy_result.get("detected_entities", []),
        },
    }

    elapsed_ms = (datetime.utcnow() - start).total_seconds() * 1000.0
    rows = _load_interactions()
    rows.append(
        {
            "timestamp": datetime.utcnow().isoformat(),
            "query": safe_query,
            "answer": final_answer,
            "agent": final_payload["agent"],
            "category": detect_category(safe_query),
            "escalated": final_payload["escalated"],
            "is_fraud": final_payload["agent"] == "blocked",
            "sentiment": final_payload.get("sentiment") or "neutral",
            "answer_quality": final_payload["evaluation"]["quality_score"],
            "relevance_score": final_payload["evaluation"]["relevance_score"],
            "faithfulness_score": final_payload["evaluation"]["faithfulness_score"],
            "hallucination_rate": final_payload["evaluation"]["hallucination_rate"],
            "compliance_score": final_payload["evaluation"]["compliance_score"],
            "response_time_ms": round(elapsed_ms, 2),
            "privacy_entities": privacy_result.get("detected_entities", []),
        }
    )
    _save_interactions(rows)

    return final_payload


@app.get("/web/analytics/summary")
def web_analytics_summary():
    rows = _load_interactions()
    return _analytics_summary(rows)


@app.get("/web/analytics/data")
def web_analytics_data():
    rows = _load_interactions()
    return {"rows": rows}


@app.post("/web/analytics/copilot")
def web_analytics_copilot(payload: CopilotQuestionRequest):
    summary = _analytics_summary(_load_interactions())
    return {"answer": _copilot_answer(payload.question, summary, mode="analytics")}


@app.post("/web/analytics/chat")
def web_analytics_chat(payload: CopilotQuestionRequest):
    summary = _analytics_summary(_load_interactions())
    return {"answer": _copilot_answer(payload.question, summary, mode="analytics")}


@app.get("/web/governance/summary")
def web_governance_summary():
    rows = _load_interactions()
    return _governance_summary(rows)


@app.post("/web/governance/copilot")
def web_governance_copilot(payload: CopilotQuestionRequest):
    summary = _governance_summary(_load_interactions())
    return {"answer": _copilot_answer(payload.question, summary, mode="governance")}


@app.post("/web/governance/chat")
def web_governance_chat(payload: CopilotQuestionRequest):
    summary = _governance_summary(_load_interactions())
    return {"answer": _copilot_answer(payload.question, summary, mode="governance")}

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

@app.get("/analytics/legacy", dependencies=[Depends(authenticate)])
def get_analytics():
    return orchestrator.get_analytics() if hasattr(orchestrator, "get_analytics") else {}
