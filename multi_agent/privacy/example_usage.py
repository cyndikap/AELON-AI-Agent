from multi_agent.privacy.privacy_agent import PrivacyAgent


def run_example() -> None:
    privacy_agent = PrivacyAgent()

    sample_text = (
        "Bonjour, je m'appelle Cynthia Sileu. "
        "Mon email est cynthia@gmail.com. "
        "Ma carte bancaire est 4978 1234 5678 9012."
    )

    result = privacy_agent.process(sample_text, language="fr")

    print("Original:")
    print(result["original_text"])
    print("\nAnonymized:")
    print(result["anonymized_text"])
    print("\nDetected entities:")
    for entity in result["detected_entities"]:
        print(entity)


if __name__ == "__main__":
    run_example()
