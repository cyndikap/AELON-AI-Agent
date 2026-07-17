# Privacy Agent (Presidio)

This module adds a privacy-first step to the AELON multi-agent flow.

## Flow

User
-> PrivacyAgent
-> FraudAgent
-> SentimentAgent
-> MemoryAgent
-> RetrievalAgent
-> L0/L1
-> ComplianceAgent
-> Response

## What is protected

- Dashboard records (query/response)
- Conversation history in Streamlit session state
- MemoryAgent storage
- API log persistence
- ChromaDB document text and metadata
- Embedding query text in RAG search

## Files changed for integration

- `multi_agent/privacy/privacy_agent.py`
- `ui/app.py`
- `api/main.py`
- `multi_agent/orchestrator.py`
- `multi_agent/memory/memory_agent.py`
- `etl/load.py`
- `rag_layer.py`

## Example usage

```python
from multi_agent.privacy.privacy_agent import PrivacyAgent

agent = PrivacyAgent()
result = agent.process(
    "Bonjour, je m'appelle Cynthia Sileu. Mon email est cynthia@gmail.com.",
    language="fr",
)

print(result["anonymized_text"])
# Bonjour, je m'appelle [PERSON]. Mon email est [EMAIL_ADDRESS].
```
