from typing import Any


class ExplainabilityAgent:
    """Builds concise, human-readable explanations for response decisions."""

    def explain(
        self,
        user_query: str,
        response: str,
        agent_used: str,
        escalated: bool,
        escalation_reason: Any = None,
        retrieved_context: list[str] | None = None,
        quality_score: float | None = None,
    ) -> str:
        reasons: list[str] = []

        if escalated:
            reason_text = str(escalation_reason or "besoin d'expertise")
            reasons.append(f"Escalade vers {agent_used} ({reason_text}).")
        else:
            reasons.append(f"Réponse traitée par {agent_used} sans escalade.")

        context_count = len(retrieved_context or [])
        if context_count > 0:
            reasons.append(f"Contexte retrieval injecté ({context_count} source(s)).")
        else:
            reasons.append("Aucun contexte retrieval exploitable trouvé.")

        if quality_score is not None:
            reasons.append(f"Qualité estimée: {float(quality_score):.1f}/100.")

        if user_query:
            reasons.append("Réponse générée à partir de l'intention détectée dans la requête utilisateur.")

        return " ".join(reasons)
