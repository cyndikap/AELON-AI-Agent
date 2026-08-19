from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Iterable

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class EvaluationWeights:
    """Weights used to compute the final answer quality score."""

    relevance: float = 0.40
    faithfulness: float = 0.30
    compliance: float = 0.20
    completeness: float = 0.10


class EvaluationAgent:
    """Evaluates a generated answer across relevance, faithfulness and safety."""

    SENSITIVE_PATTERNS = [
        re.compile(r"\botp\b", flags=re.IGNORECASE),
        re.compile(r"\bcode\s*secret\b", flags=re.IGNORECASE),
        re.compile(r"\bmot\s*de\s*passe\b", flags=re.IGNORECASE),
        re.compile(r"\bpassword\b", flags=re.IGNORECASE),
        re.compile(r"\b(?:\d[ -]*?){13,19}\b"),
    ]

    def __init__(self, weights: EvaluationWeights | None = None) -> None:
        self.weights = weights or EvaluationWeights()

    def evaluate(self, question: str, answer: str, retrieved_docs: list[str]):
        """Return quality metrics for a generated answer.

        Args:
            question: User question.
            answer: Model answer.
            retrieved_docs: RAG chunks used to generate the answer.

        Returns:
            Dict with relevance_score, faithfulness_score, hallucination_rate,
            answer_quality, compliance_score.
        """
        try:
            safe_question = (question or "").strip()
            safe_answer = (answer or "").strip()
            docs = [str(d).strip() for d in (retrieved_docs or []) if str(d).strip()]

            relevance_score = self._compute_relevance(safe_question, safe_answer)
            faithfulness_score = self._compute_faithfulness(safe_answer, docs)
            hallucination_rate = max(0.0, min(100.0, 100.0 - faithfulness_score))
            compliance_score = self._compute_compliance(safe_answer)
            completeness_score = self._compute_completeness(safe_answer)

            answer_quality = (
                self.weights.relevance * relevance_score
                + self.weights.faithfulness * faithfulness_score
                + self.weights.compliance * compliance_score
                + self.weights.completeness * completeness_score
            )

            result = {
                "relevance_score": round(relevance_score, 2),
                "faithfulness_score": round(faithfulness_score, 2),
                "hallucination_rate": round(hallucination_rate, 2),
                "answer_quality": round(max(0.0, min(100.0, answer_quality)), 2),
                "compliance_score": round(compliance_score, 2),
            }
            LOGGER.info("Evaluation computed: %s", result)
            return result
        except Exception as exc:
            LOGGER.exception("Evaluation failure: %s", exc)
            return {
                "relevance_score": 0.0,
                "faithfulness_score": 0.0,
                "hallucination_rate": 100.0,
                "answer_quality": 0.0,
                "compliance_score": 0.0,
            }

    def _compute_relevance(self, question: str, answer: str) -> float:
        if not question or not answer:
            return 0.0

        similarity = self._tfidf_similarity(question, answer)
        return max(0.0, min(100.0, similarity * 100.0))

    def _compute_faithfulness(self, answer: str, retrieved_docs: list[str]) -> float:
        if not answer:
            return 0.0
        if not retrieved_docs:
            return 0.0

        answer_sentences = [s.strip() for s in re.split(r"[.!?]\s+", answer) if s.strip()]
        if not answer_sentences:
            answer_sentences = [answer]

        support_scores: list[float] = []
        for sentence in answer_sentences:
            sims = [self._tfidf_similarity(sentence, doc) for doc in retrieved_docs]
            max_support = max(sims) if sims else 0.0
            support_scores.append(max_support)

        avg_support = sum(support_scores) / len(support_scores)
        return max(0.0, min(100.0, avg_support * 100.0))

    def _compute_compliance(self, answer: str) -> float:
        if not answer:
            return 0.0

        hits = 0
        for pattern in self.SENSITIVE_PATTERNS:
            if pattern.search(answer):
                hits += 1

        if hits == 0:
            return 100.0

        penalty = min(95.0, 35.0 * hits)
        return max(5.0, 100.0 - penalty)

    def _compute_completeness(self, answer: str) -> float:
        words = re.findall(r"\b\w+\b", answer)
        word_count = len(words)

        if word_count == 0:
            return 0.0

        if word_count < 12:
            base = 35.0
        elif word_count < 25:
            base = 65.0
        elif word_count <= 220:
            base = 100.0
        else:
            base = 80.0

        # Encourage operational answers with multiple action points.
        action_markers = len(re.findall(r"\b(1\.|2\.|3\.|step|etape|étape|d'abord|ensuite|finally)\b", answer, flags=re.IGNORECASE))
        bonus = min(10.0, float(action_markers) * 2.5)
        return max(0.0, min(100.0, base + bonus))

    @staticmethod
    def _tfidf_similarity(left: str, right: str) -> float:
        if not left or not right:
            return 0.0

        vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words=None)
        matrix = vectorizer.fit_transform([left, right])
        similarity_matrix = cosine_similarity(matrix[0:1], matrix[1:2])
        return float(similarity_matrix[0][0])

    @staticmethod
    def flatten_docs(items: Iterable[str]) -> list[str]:
        """Utility helper to normalize docs passed from multiple providers."""
        return [str(item).strip() for item in items if str(item).strip()]
