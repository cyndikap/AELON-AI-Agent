class ObservabilityAgent:

    def analyze(self, response, context):
        issues = []

        # réponse trop courte
        if len(response.split()) < 10:
            issues.append("Réponse trop courte")

        #  mot générique
        generic_words = ["je ne sais pas", "désolé", "je ne peux pas"]
        if any(w in response.lower() for w in generic_words):
            issues.append("Réponse générique")

        # escalade répétée
        if context.get("escalated_count", 0) > 3:
            issues.append("Trop d'escalades")

        score = 100 - (len(issues) * 20)

        return {
            "quality_score": score,
            "issues": issues
        }
