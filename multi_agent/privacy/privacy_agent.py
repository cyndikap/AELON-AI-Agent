import re
from typing import Any, Dict, List

from presidio_analyzer import AnalyzerEngine, Pattern, PatternRecognizer
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig


class PrivacyAgent:
    """Detects and anonymizes sensitive entities before downstream processing."""

    NLP_CONFIGURATION = {
        "nlp_engine_name": "spacy",
        "models": [
            {"lang_code": "en", "model_name": "en_core_web_sm"},
            {"lang_code": "fr", "model_name": "fr_core_news_sm"},
        ],
    }

    SUPPORTED_ENTITIES = [
        "PERSON",
        "EMAIL_ADDRESS",
        "PHONE_NUMBER",
        "CREDIT_CARD",
        "IBAN_CODE",
        "LOCATION",
        "DATE_TIME",
        "BANK_ACCOUNT",
    ]

    def __init__(self) -> None:
        provider = NlpEngineProvider(nlp_configuration=self.NLP_CONFIGURATION)
        nlp_engine = provider.create_engine()
        self.analyzer = AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=["en", "fr"])
        self.anonymizer = AnonymizerEngine()
        self._register_custom_recognizers()

    def _register_custom_recognizers(self) -> None:
        # Robust card and IBAN detection independent of language model quality.
        credit_card_pattern = Pattern(
            name="credit_card_pattern",
            regex=r"\b(?:\d[ -]*?){13,19}\b",
            score=0.8,
        )
        iban_pattern = Pattern(
            name="iban_pattern",
            regex=r"\b[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b",
            score=0.8,
        )
        bank_account_pattern = Pattern(
            name="bank_account_pattern",
            regex=r"\b\d{8,20}\b",
            score=0.45,
        )

        self.analyzer.registry.add_recognizer(
            PatternRecognizer(
                supported_entity="CREDIT_CARD",
                patterns=[credit_card_pattern],
            )
        )
        self.analyzer.registry.add_recognizer(
            PatternRecognizer(
                supported_entity="IBAN_CODE",
                patterns=[iban_pattern],
            )
        )
        self.analyzer.registry.add_recognizer(
            PatternRecognizer(
                supported_entity="BANK_ACCOUNT",
                patterns=[bank_account_pattern],
            )
        )

    def process_text(self, text: str, language: str = "en") -> Dict[str, Any]:
        original_text = str(text or "")
        if not original_text.strip():
            return {
                "original_text": original_text,
                "anonymized_text": original_text,
                "detected_entities": [],
            }

        try:
            results = self.analyzer.analyze(
                text=original_text,
                entities=self.SUPPORTED_ENTITIES,
                language=language,
            )
        except Exception:
            # Presidio defaults to English NLP assets; fall back if language model is unavailable.
            fallback_language = "en"
            results = self.analyzer.analyze(
                text=original_text,
                entities=self.SUPPORTED_ENTITIES,
                language=fallback_language,
            )

        operators = {
            entity: OperatorConfig("replace", {"new_value": f"[{entity}]"})
            for entity in self.SUPPORTED_ENTITIES
        }

        anonymized = self.anonymizer.anonymize(
            text=original_text,
            analyzer_results=results,
            operators=operators,
        )

        entities = [
            {
                "entity_type": item.entity_type,
                "start": item.start,
                "end": item.end,
                "score": round(float(item.score), 4),
            }
            for item in results
        ]

        return {
            "original_text": original_text,
            "anonymized_text": anonymized.text,
            "detected_entities": entities,
        }

    def process(self, text: str, language: str = "en") -> Dict[str, Any]:
        return self.process_text(text=text, language=language)

    @staticmethod
    def mask_email_for_preview(text: str) -> str:
        return re.sub(r"([\w\.-]+)@([\w\.-]+)", "[EMAIL_ADDRESS]", str(text or ""))
