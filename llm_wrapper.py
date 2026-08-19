# llm_wrapper.py

import os
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()


class AzureChatLLM:
    """Thin Azure OpenAI wrapper used by the app and tests."""

    def __init__(self):
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        version = os.getenv("AZURE_OPENAI_API_VERSION")
        deployment = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT")

        missing = [
            name for name, value in {
                "AZURE_OPENAI_API_KEY": api_key,
                "AZURE_OPENAI_ENDPOINT": endpoint,
                "AZURE_OPENAI_API_VERSION": version,
                "AZURE_OPENAI_CHAT_DEPLOYMENT": deployment,
            }.items() if not value
        ]
        if missing:
            raise RuntimeError(f"Missing Azure Chat env vars: {missing}")

        self.deployment = deployment
        self.client = AzureOpenAI(
            api_key=api_key,
            azure_endpoint=endpoint,
            api_version=version,
        )

    def __call__(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.deployment,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a banking support assistant. "
                        "Answer using only the supplied context and stay in the same language as the user."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=250,
        )
        content = response.choices[0].message.content
        return str(content or "").strip()


def llm(prompt: str) -> str:
    """Compatibility entrypoint for production Azure-backed chat calls."""
    return AzureChatLLM()(prompt)
