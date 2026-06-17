import os
from openai import AzureOpenAI
from dotenv import load_dotenv

from pathlib import Path
load_dotenv(Path(__file__).resolve().parent / "multi_agent" / ".env")



class AzureChatLLM:
    """
    Thin wrapper for Azure OpenAI ChatCompletion.
    Designed to be injected into agents as llm_callable(prompt:str)->str
    """

    def __init__(self):
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        version = os.getenv("AZURE_OPENAI_API_VERSION")
        deployment = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT")

        missing = [k for k, v in {
            "AZURE_OPENAI_API_KEY": api_key,
            "AZURE_OPENAI_ENDPOINT": endpoint,
            "AZURE_OPENAI_API_VERSION": version,
            "AZURE_OPENAI_CHAT_DEPLOYMENT": deployment,
        }.items() if not v]

        if missing:
            raise RuntimeError(f"Missing Azure Chat env vars: {missing}")

        self.deployment = deployment
        self.client = AzureOpenAI(
            api_key=api_key,
            azure_endpoint=endpoint,
            api_version=version
        )

    def __call__(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.deployment,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an L0 banking support agent. "
                        "You must base your answers strictly on the provided knowledge base. "
                        "If there is insufficient evidence, say so explicitly. "
                        "Provide clear, actionable recommendations."
                        "Always respond in the same language as the user's question."
                    ),
                },
                {
                    
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,
            max_tokens=250
        )

        return response.choices[0].message.content.strip()
