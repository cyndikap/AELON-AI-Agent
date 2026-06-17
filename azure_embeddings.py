import os
from openai import AzureOpenAI
from dotenv import load_dotenv
load_dotenv()

class AzureEmbeddingClient:
    def __init__(self):
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        version = os.getenv("AZURE_OPENAI_API_VERSION")
        deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")

        missing = [
            name for name, val in {
                "AZURE_OPENAI_API_KEY": api_key,
                "AZURE_OPENAI_ENDPOINT": endpoint,
                "AZURE_OPENAI_API_VERSION": version,
                "AZURE_OPENAI_DEPLOYMENT": deployment,
            }.items() if not val
        ]

        if missing:
            raise RuntimeError(f"Missing Azure OpenAI env vars: {missing}")

        self.deployment = deployment
        self.client = AzureOpenAI(
            api_key=api_key,
            azure_endpoint=endpoint,
            api_version=version
        )

    def embed(self, texts: list[str]):
        response = self.client.embeddings.create(
            model=self.deployment,
            input=texts
        )
        return [d.embedding for d in response.data]
