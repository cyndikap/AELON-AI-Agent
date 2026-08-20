from __future__ import annotations

import csv
import json
import logging
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

from multi_agent.evaluation.rag_evaluation_service import RAGEvaluationService
from multi_agent.orchestrator import Orchestrator
from utils.category_detector import detect_category

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

LOGGER = logging.getLogger("aelon.rag_evaluation_runner")
DEFAULT_DATASET_PATH = Path("data") / "reference" / "rag_reference_questions.json"
EVALUATION_EXPORT_PATH = PROJECT_ROOT / "evaluation_details.csv"

METIER_SYNONYMS = {
    "virement": ["virement", "transfert", "transfer"],
    "fraude": ["fraude", "phishing", "arnaque", "escroquerie", "operation non autorisee", "operation non autorisee"],
    "carte": ["carte", "cb", "carte bancaire", "credit card", "debit card"],
    "rgpd": ["rgpd", "donnees personnelles", "donnee personnelle", "privacy", "confidentialite", "protection des donnees"],
    "kyc": ["kyc", "connaissance client", "verification d identite", "piece d identite", "justificatif de domicile"],
    "conformite": ["conformite", "compliance", "lcb ft", "lcbft", "blanchiment", "tracfin", "acpr"],
    "suppression": ["suppression", "effacement", "retirer", "supprimer"],
    "identite": ["identite", "identity", "identification"],
    "donnees": ["donnees", "donnee", "data"],
}


def _normalize_text(value: str) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(character for character in text if not unicodedata.combining(character))
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _apply_synonyms(text: str) -> str:
    normalized = _normalize_text(text)
    for canonical, variants in sorted(METIER_SYNONYMS.items(), key=lambda item: len(item[0]), reverse=True):
        for variant in sorted(variants, key=len, reverse=True):
            normalized = normalized.replace(_normalize_text(variant), canonical)
    return normalized


def _source_match_rate(expected_sources: list[str], retrieved_sources: list[str]) -> float:
    expected = [_normalize_text(item) for item in expected_sources if str(item).strip()]
    retrieved = [_normalize_text(item) for item in retrieved_sources if str(item).strip()]
    if not expected:
        return 1.0
    if not retrieved:
        return 0.0

    matched = 0
    for expected_item in expected:
        if any(expected_item in source or source in expected_item for source in retrieved):
            matched += 1
    return matched / len(expected)


def _keyword_match_rate(expected_keywords: list[str], answer: str) -> float:
    expected = [_apply_synonyms(item) for item in expected_keywords if str(item).strip()]
    answer_text = _apply_synonyms(answer)
    if not expected:
        return 1.0
    if not answer_text:
        return 0.0

    matched = sum(1 for keyword in expected if keyword in answer_text)
    return matched / len(expected)


def _export_evaluation_details(details: list[dict], export_path: Path = EVALUATION_EXPORT_PATH) -> None:
    export_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "question",
        "expected_category",
        "retrieved_category",
        "category_match",
        "source_match_rate",
        "keyword_match_rate",
    ]
    with export_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for detail in details:
            writer.writerow({
                "question": detail.get("question", ""),
                "expected_category": detail.get("expected_category", ""),
                "retrieved_category": detail.get("predicted_category", ""),
                "category_match": int(detail.get("category_match", 0) or 0),
                "source_match_rate": round(float(detail.get("source_match_rate", 0.0) or 0.0), 2),
                "keyword_match_rate": round(float(detail.get("keyword_match_rate", 0.0) or 0.0), 2),
            })


def load_reference_questions(dataset_path: str | None = None) -> list[dict]:
    target = Path(dataset_path) if dataset_path else DEFAULT_DATASET_PATH
    with target.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return payload if isinstance(payload, list) else []


def evaluate_reference_questions(
    dataset_path: str | None = None,
    dataset_name: str = "rag_reference_questions",
    max_questions: int | None = None,
) -> dict:
    questions = load_reference_questions(dataset_path)
    if max_questions is not None:
        questions = questions[:max_questions]

    orchestrator = Orchestrator()
    service = RAGEvaluationService()
    service.ensure_table()

    executed_at = datetime.now(timezone.utc).isoformat()
    processed = 0
    saved = 0
    failures = 0

    for item in questions:
        question = str(item.get("question") or "").strip()
        if not question:
            continue

        try:
            response = orchestrator.handle_user_query(question, user_session_id="rag-eval-batch")
            retrieval_rows = response.get("retrieval", {}).get("result", {}).get("data_array", [])
            sources_payload = response.get("sources", [])
            categories = [entry.get("categorie", "") for entry in sources_payload if isinstance(entry, dict)]
            retrieved_sources = [entry.get("source", "") for entry in sources_payload if isinstance(entry, dict)]
            predicted_category = detect_category(question)
            evaluation_metrics = response.get("evaluation", {}) if isinstance(response.get("evaluation"), dict) else {}
            expected_sources = item.get("expected_sources") or []
            expected_keywords = item.get("expected_keywords") or []
            answer_text = response.get("answer") or response.get("response") or ""

            expected_category = str(item.get("expected_category", "autre"))
            category_match = 1 if _normalize_text(expected_category) == _normalize_text(predicted_category) else 0
            source_match_rate = _source_match_rate(expected_sources, retrieved_sources)
            keyword_match_rate = _keyword_match_rate(expected_keywords, answer_text)

            payload = {
                "executed_at": executed_at,
                "dataset_name": dataset_name,
                "question_id": item.get("question_id", f"Q{processed+1:03d}"),
                "question": question,
                "expected_category": expected_category,
                "predicted_category": predicted_category,
                "reference_answer": item.get("expected_answer") or item.get("reference_answer") or "",
                "answer": answer_text,
                "expected_sources": expected_sources,
                "expected_keywords": expected_keywords,
                "sources": retrieved_sources,
                "categories": categories,
                "category_match": category_match,
                "source_match_rate": source_match_rate,
                "keyword_match_rate": keyword_match_rate,
                "retrieval_count": len(retrieval_rows),
                "retrieval_success": 1 if len(retrieval_rows) > 0 else 0,
                "response_time_ms": float(response.get("response_time_ms") or 0.0),
                "relevance_score": float(evaluation_metrics.get("relevance_score") or 0.0),
                "faithfulness_score": float(evaluation_metrics.get("faithfulness_score") or 0.0),
                "hallucination_rate": float(evaluation_metrics.get("hallucination_rate") or 0.0),
                "answer_quality": float(evaluation_metrics.get("answer_quality") or 0.0),
                "compliance_score": float(evaluation_metrics.get("compliance_score") or 0.0),
            }
            service.save_result(payload)
            saved += 1
        except Exception as exc:
            LOGGER.exception("rag_evaluation.failed question=%s error=%s", question, exc)
            failures += 1
        finally:
            processed += 1

    result = {
        "processed": processed,
        "saved": saved,
        "failures": failures,
        "executed_at": executed_at,
        "summary": service.latest_summary(),
    }

    try:
        _export_evaluation_details(service.latest_details())
        result["export_path"] = str(EVALUATION_EXPORT_PATH)
    except Exception as exc:
        LOGGER.exception("rag_evaluation.export_failed error=%s", exc)
        result["export_path"] = None

    return result


if __name__ == "__main__":
    print(json.dumps(evaluate_reference_questions(), ensure_ascii=False, indent=2))
