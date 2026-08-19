# 
AV Bancaire Multi-Agents

This project's goal is to build a multi agent system aiming at the resolution of technical issues encountered by the clients in the banking sector.

## Local Environment

Use the repository virtual environment only.

### Bootstrap

```powershell
Set-Location C:/Users/csileuka/OneDrive - Capgemini/Bureau/PROJETS/AI.Agent.AELON/GEN.AI
powershell -ExecutionPolicy Bypass -File .\scripts\bootstrap-ui.ps1
```

### Run the UI

```powershell
Set-Location C:/Users/csileuka/OneDrive - Capgemini/Bureau/PROJETS/AI.Agent.AELON/GEN.AI
powershell -ExecutionPolicy Bypass -File .\scripts\run-ui.ps1
```

The web UI is served by FastAPI on `http://127.0.0.1:8010/`.

### Notes

- The workspace is configured to use `.venv` as the default interpreter.
- `PYTHONNOUSERSITE=1` is enforced to prevent conflicts with packages installed under AppData.
- Privacy dependencies are installed in the local environment together with the required spaCy models.

## Current Platform Scope

The AELON platform now includes a production-ready RAG support flow for banking conversations:

- Bronze, Silver, and Gold data layers
- Chunking and Databricks embeddings with `databricks-gte-large-en`
- Databricks Vector Search retrieval
- Retrieval agent plugged into the orchestrator
- LLM answer generation grounded on retrieved document chunks
- Automatic conversation persistence in Databricks
- Analytics and Governance KPI pipelines
- FastAPI-based dashboards and KPI APIs

## Runtime Flow

```text
User
-> Orchestrator
-> Retrieval Agent
-> Databricks Vector Search
-> Top Chunks
-> LLM
-> Response
-> Conversation Logger
-> fr_raise.rag_pipeline.gold_conversations
-> Analytics / Governance KPIs
```

## Databricks Tables

Operational RAG tables:

- `fr_raise.rag_pipeline.bronze_documents`
- `fr_raise.rag_pipeline.silver_documents`
- `fr_raise.rag_pipeline.gold_documents`
- `fr_raise.rag_pipeline.gold_embeddings`
- `fr_raise.rag_pipeline.gold_conversations`
- `fr_raise.rag_pipeline.gold_governance`

KPI tables:

- `fr_raise.rag_pipeline.analytics_metrics`
- `fr_raise.rag_pipeline.governance_metrics`

## Key Environment Variables

The following variables are required for the full production flow:

```env
DATABRICKS_HOST=...
DATABRICKS_TOKEN=...
DATABRICKS_SQL_WAREHOUSE_ID=...
DATABRICKS_CATALOG=fr_raise
DATABRICKS_SCHEMA=rag_pipeline

AZURE_OPENAI_ENDPOINT=...
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_CHAT_DEPLOYMENT=...

AZURE_AI_SEARCH_INDEX_NAME=...
AZURE_AI_SEARCH_API_KEY=...
```

Without `DATABRICKS_SQL_WAREHOUSE_ID`, the application falls back to local failed-event buffering instead of writing directly to `gold_conversations`.

## Main APIs

User and dashboards:

- `POST /web/chat`
- `GET /dashboards/analytics`
- `GET /dashboards/governance`

KPI JSON APIs:

- `GET /analytics`
- `GET /governance`

Legacy / internal endpoints are still present in `api/main.py`.

## Conversation Persistence

Each generated answer is persisted through `multi_agent/conversation_logger.py` with the following payload:

- `conversation_id`
- `timestamp`
- `question`
- `answer`
- `sources`
- `categories`
- `retrieval_count`
- `response_time_ms`
- `user_session_id`

If the SQL warehouse is unavailable, events are buffered in:

- `data/processed/failed_conversation_events.jsonl`

Replay is supported with:

```powershell
Set-Location C:/Users/csileuka/OneDrive - Capgemini/Bureau/PROJETS/AI.Agent.AELON/GEN.AI
.\.venv\Scripts\python.exe .\scripts\replay_failed_conversations.py
```

## KPI Jobs

SQL assets used to provision and populate KPI tables:

- `sql/analytics_metrics.sql`
- `sql/governance_metrics.sql`
- `sql/analytics_kpis.sql`
- `sql/governance_kpis.sql`

Databricks notebooks:

- `notebooks/05_analytics_metrics.ipynb`
- `notebooks/06_governance_metrics.ipynb`

## Monitoring

The platform emits structured logs for:

- `orchestrator.start`
- `orchestrator.end`
- `retrieval.start`
- `retrieval.documents_found`
- `retrieval.sources`
- `retrieval.response_time`
- `retrieval.end`
- `llm.start`
- `llm.end`
- `conversation.saved`

## Quick Start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn api.main:app --host 127.0.0.1 --port 8010 --reload
```