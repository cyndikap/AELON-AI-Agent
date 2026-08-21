import re
import unicodedata
from dataclasses import dataclass


@dataclass(frozen=True)
class SentimentLanguageProfile:
    language_code: str
    language_name: str
    sentiment: str
    tone_hint: str
    opening: str


class SentimentLanguageAgent:
    """Detects conversation language and user emotional tone before response generation."""

    SUPPORTED_LANGUAGES = {
        "fr": "Français",
        "en": "English",
        "es": "Español",
        "de": "Deutsch",
        "it": "Italiano",
        "ar": "العربية",
    }

    SENTIMENT_OPENINGS = {
        "fr": {
            "Frustré": "Je comprends votre frustration. Cette situation peut etre genante.",
            "Inquiet": "Je comprends votre inquietude. Si vous suspectez un risque, il est important d agir rapidement.",
            "Satisfait": "Ravi d avoir pu vous aider. N hésitez pas a revenir si vous avez d autres questions.",
            "Urgent": "Cette situation nécessite une action rapide. Voici les demarches a effectuer immediatement.",
            "Neutre": "Voici les informations utiles pour votre demande.",
        },
        "en": {
            "Frustré": "I understand your frustration. This situation can be inconvenient.",
            "Inquiet": "I understand your concern. If you suspect a risk, it is important to act quickly.",
            "Satisfait": "I am glad I could help. Feel free to return if you have more questions.",
            "Urgent": "This situation requires immediate action. Here are the steps to take right away.",
            "Neutre": "Here is the relevant information for your request.",
        },
        "es": {
            "Frustré": "Entiendo su frustracion. Esta situacion puede ser molesta.",
            "Inquiet": "Entiendo su preocupacion. Si sospecha un riesgo, es importante actuar rapidamente.",
            "Satisfait": "Me alegra haber podido ayudarle. No dude en volver si tiene mas preguntas.",
            "Urgent": "Esta situacion requiere una accion rapida. Aqui tiene los pasos inmediatos.",
            "Neutre": "Aqui tiene la informacion relevante para su solicitud.",
        },
        "de": {
            "Frustré": "Ich verstehe Ihre Frustration. Diese Situation kann belastend sein.",
            "Inquiet": "Ich verstehe Ihre Sorge. Bei Verdacht auf ein Risiko sollten Sie schnell handeln.",
            "Satisfait": "Es freut mich, dass ich helfen konnte. Melden Sie sich gern bei weiteren Fragen.",
            "Urgent": "Diese Situation erfordert schnelles Handeln. Hier sind die sofortigen Schritte.",
            "Neutre": "Hier sind die relevanten Informationen zu Ihrer Anfrage.",
        },
        "it": {
            "Frustré": "Capisco la sua frustrazione. Questa situazione puo essere difficile.",
            "Inquiet": "Capisco la sua preoccupazione. Se sospetta un rischio, e importante agire rapidamente.",
            "Satisfait": "Sono lieto di averla aiutata. Torni pure se ha altre domande.",
            "Urgent": "Questa situazione richiede un azione rapida. Ecco i passaggi immediati.",
            "Neutre": "Ecco le informazioni utili per la sua richiesta.",
        },
        "ar": {
            "Frustré": "اتفهم شعورك بالاحباط. هذا الموقف قد يكون مزعجا.",
            "Inquiet": "اتفهم قلقك. اذا كان هناك اشتباه بمخاطر فمن المهم التصرف بسرعة.",
            "Satisfait": "يسعدني انني استطعت مساعدتك. لا تتردد في العودة اذا كانت لديك اسئلة اخرى.",
            "Urgent": "هذا الوضع يتطلب اجراء سريعا. اليك الخطوات الفورية.",
            "Neutre": "اليك المعلومات المناسبة لطلبك.",
        },
    }

    LANGUAGE_HINTS = {
        "fr": ["bonjour", "comment", "virement", "carte", "compte", "fraude", "merci"],
        "en": ["how", "transfer", "card", "account", "fraud", "please", "thanks"],
        "es": ["como", "cómo", "puedo", "cancelar", "tarjeta", "transferencia", "cuenta", "fraude", "gracias"],
        "de": ["wie", "kann", "ich", "meine", "karte", "sperren", "uberweisung", "konto", "betrug", "danke"],
        "it": ["come", "carta", "bonifico", "conto", "frode", "grazie"],
        "ar": ["كيف", "يمكنني", "بطاقة", "تحويل", "حساب", "احتيال", "الإبلاغ", "عملية", "مصرفي", "شكرا"],
    }

    SENTIMENT_PATTERNS = {
        "Urgent": [
            r"\burgent\b", r"\bimmediat\w*\b", r"\bmaintenant\b", r"\b5 minutes\b",
            r"\bnow\b", r"\bimmediately\b", r"\basap\b", r"\bahora\b", r"\bsofort\b",
            r"\bsubito\b", r"\bفورا\b", r"\bحال\b",
        ],
        "Frustré": [
            r"\bbloqu[eé]\b", r"\bmarre\b", r"\bimpossible\b", r"\b3 jours\b", r"\berreur\b",
            r"\bblocked\b", r"\bannoy\w*\b", r"\bstill not\b", r"\bfrustrat\w*\b",
            r"\bbloquead\w*\b", r"\bgesperrt\b", r"\bfrust\w*\b", r"\bbloccat\w*\b", r"\bمشكلة\b",
        ],
        "Inquiet": [
            r"\bfraude\b", r"\bpeur\b", r"\binquiet\w*\b", r"\bsuspect\w*\b", r"\bvol\w*\b",
            r"\bfraud\b", r"\bworried\b", r"\bconcern\w*\b", r"\bstolen\b",
            r"\bfraude\b", r"\bpreocup\w*\b", r"\bbetrug\b", r"\bsorge\w*\b", r"\bpreoccup\w*\b", r"\bقلق\b", r"\bاحتيال\b",
        ],
        "Satisfait": [
            r"\bmerci\b", r"\bparfait\b", r"\bsuper\b", r"\bthanks\b", r"\bgreat\b", r"\bhelped\b",
            r"\bgracias\b", r"\bperfecto\b", r"\bdanke\b", r"\bgut\b", r"\bgrazie\b", r"\bottimo\b", r"\bشكرا\b",
        ],
    }

    def __init__(self):
        self._session_language: dict[str, str] = {}

    @staticmethod
    def _normalize(text: str) -> str:
        return str(text or "").strip()

    @staticmethod
    def _strip_accents(text: str) -> str:
        normalized = unicodedata.normalize("NFKD", text)
        return "".join(ch for ch in normalized if not unicodedata.combining(ch))

    def _detect_language(self, text: str) -> str:
        if re.search(r"[\u0600-\u06FF]", text):
            return "ar"

        lowered = text.lower()
        folded = self._strip_accents(lowered)
        scores = {code: 0 for code in self.SUPPORTED_LANGUAGES}

        for code, keywords in self.LANGUAGE_HINTS.items():
            for token in keywords:
                token_folded = self._strip_accents(token.lower())
                if token in lowered or token_folded in folded:
                    scores[code] += 1

        if any(ch in lowered for ch in ("é", "è", "à", "ç", "ô", "ù")):
            scores["fr"] += 2
        if any(ch in lowered for ch in ("¿", "¡", "ñ")):
            scores["es"] += 3
        if any(ch in lowered for ch in ("ä", "ö", "ü", "ß")):
            scores["de"] += 3

        best = max(scores.items(), key=lambda item: item[1])
        return best[0] if best[1] > 0 else "fr"

    def _detect_sentiment(self, text: str) -> str:
        lowered = text.lower()

        for label in ("Urgent", "Frustré", "Inquiet", "Satisfait"):
            patterns = self.SENTIMENT_PATTERNS.get(label, [])
            if any(re.search(pattern, lowered) for pattern in patterns):
                return label

        return "Neutre"

    @staticmethod
    def _tone_hint(sentiment: str) -> str:
        if sentiment == "Urgent":
            return "calme, prioritaire et orientee action"
        if sentiment == "Frustré":
            return "empathique, rassurante et concise"
        if sentiment == "Inquiet":
            return "rassurante, factuelle et protectrice"
        if sentiment == "Satisfait":
            return "positive et professionnelle"
        return "professionnelle, concise et courtoise"

    def analyze(self, user_query: str, session_id: str = "anonymous") -> SentimentLanguageProfile:
        text = self._normalize(user_query)
        session_key = str(session_id or "anonymous").strip() or "anonymous"

        language_code = self._session_language.get(session_key)
        if not language_code:
            language_code = self._detect_language(text)
            if language_code not in self.SUPPORTED_LANGUAGES:
                language_code = "fr"
            self._session_language[session_key] = language_code

        sentiment = self._detect_sentiment(text)
        opening = self.SENTIMENT_OPENINGS.get(language_code, self.SENTIMENT_OPENINGS["fr"]).get(
            sentiment,
            self.SENTIMENT_OPENINGS[language_code]["Neutre"],
        )

        return SentimentLanguageProfile(
            language_code=language_code,
            language_name=self.SUPPORTED_LANGUAGES.get(language_code, "Français"),
            sentiment=sentiment,
            tone_hint=self._tone_hint(sentiment),
            opening=opening,
        )
