# -*- coding: utf-8 -*-

# Patterns de données sensibles à ne jamais exposer dans une réponse
SENSITIVE_PATTERNS = [
    "iban", "numéro de compte", "account number",
    "mot de passe", "password", "code pin", "cvv",
    "date de naissance", "date of birth", "numéro client",
    "adresse", "email", "téléphone", "phone"
]

# Règles de conformité bancaire
COMPLIANCE_RULES = [
    "Ne jamais demander ou afficher un mot de passe, code PIN ou CVV",
    "Ne jamais afficher un IBAN ou numéro de compte en clair",
    "Toujours proposer une escalade humaine pour les cas sensibles",
    "Respecter le RGPD : ne pas collecter de données sans consentement",
    "PCI-DSS : aucune donnée de carte bancaire dans les réponses",
    "DORA : garantir la traçabilité des incidents de support",
]


class ComplianceAgent:
    """
    ComplianceAgent — vérifie que la réponse LLM respecte
    RGPD, PCI-DSS et DORA avant affichage au client.
    S'applique sur la réponse L0 ou L1.
    """

    def __init__(self, llm):
        self.llm = llm

    def check(self, response: str, user_query: str) -> dict:
        # Vérification rapide par mots-clés
        response_lower = response.lower()
        sensitive_hit = [p for p in SENSITIVE_PATTERNS if p in response_lower]

        rules_text = "\n".join(f"- {r}" for r in COMPLIANCE_RULES)

        llm_output = self.llm(f"""
Tu es un agent de conformité bancaire (RGPD, PCI-DSS, DORA).

Analyse la réponse suivante générée pour un client bancaire.
Vérifie qu'elle respecte ces règles :
{rules_text}

Question du client : {user_query}
Réponse à analyser : {response}

Réponds uniquement en JSON :
{{
  "is_compliant": true | false,
  "violations": ["liste des violations détectées, vide si aucune"],
  "corrected_response": "réponse corrigée si non conforme, sinon identique à l'originale",
  "risk_level": "low" | "medium" | "high"
}}
""")

        is_compliant = (
            '"is_compliant": true' in llm_output.lower()
            and not sensitive_hit
        )

        risk_level = "low"
        if '"risk_level": "high"' in llm_output.lower() or sensitive_hit:
            risk_level = "high"
        elif '"risk_level": "medium"' in llm_output.lower():
            risk_level = "medium"

        # Extraire la réponse corrigée du JSON LLM
        corrected = response
        marker = '"corrected_response":'
        if marker in llm_output:
            try:
                start = llm_output.index(marker) + len(marker)
                snippet = llm_output[start:].strip().lstrip('"')
                end = snippet.index('",')
                corrected = snippet[:end].strip()
            except (ValueError, IndexError):
                corrected = response

        return {
            "is_compliant": is_compliant,
            "risk_level": risk_level,
            "sensitive_keywords_found": sensitive_hit,
            "corrected_response": corrected,
            "raw": llm_output,
        }
