from multi_agent.evaluation.evaluation_agent import EvaluationAgent
from multi_agent.retrieval_agent import RetrievalAgent


def test_retrieval_agent_search_matches_real_content() -> None:
    agent = RetrievalAgent([
        {"text": "client cannot login"},
        {"text": "payment failed for order #1234"},
        {"text": "how to reset my password?"},
    ])

    matches = agent.search("payment")

    assert len(matches) == 1
    assert "payment failed" in matches[0]["text"].lower()


def test_evaluate_returns_expected_keys() -> None:
    agent = EvaluationAgent()
    result = agent.evaluate(
        question="Comment réinitialiser mon mot de passe ?",
        answer="Vous pouvez réinitialiser votre mot de passe depuis l'espace client, section sécurité.",
        retrieved_docs=["Réinitialisation depuis l'espace client > sécurité > mot de passe."],
    )

    assert set(result.keys()) == {
        "relevance_score",
        "faithfulness_score",
        "hallucination_rate",
        "answer_quality",
        "compliance_score",
    }



def test_hallucination_is_inverse_of_faithfulness() -> None:
    agent = EvaluationAgent()
    result = agent.evaluate(
        question="Comment bloquer une carte ?",
        answer="Pour bloquer une carte, ouvrez l'application puis choisissez opposition carte.",
        retrieved_docs=["Depuis l'application: menu cartes, action opposition."],
    )

    assert result["hallucination_rate"] == round(100 - result["faithfulness_score"], 2)



def test_compliance_score_drops_on_sensitive_content() -> None:
    agent = EvaluationAgent()
    result = agent.evaluate(
        question="Je veux vérifier mes accès",
        answer="Donnez votre OTP et votre mot de passe ainsi que votre numéro 4111 1111 1111 1111.",
        retrieved_docs=["Le support ne doit jamais demander OTP ou mot de passe."],
    )

    assert result["compliance_score"] < 50



def test_scores_are_within_0_100() -> None:
    agent = EvaluationAgent()
    result = agent.evaluate(
        question="Question test",
        answer="Réponse test avec quelques détails utiles pour le client final.",
        retrieved_docs=["Document court de test"],
    )

    for value in result.values():
        assert 0.0 <= value <= 100.0
