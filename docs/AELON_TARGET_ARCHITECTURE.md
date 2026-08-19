# AELON Target Product Architecture

## Product Spaces

### 1) Customer Space (ROLE: CUSTOMER)
- Primary product surface: Chat only.
- Visible elements: conversation history, user messages, AI responses.
- Hidden from customer: KPI, dashboards, governance, agent internals.
- Privacy-first flow enforced before display/storage.

### 2) Business Analytics Space (ROLE: BUSINESS_ANALYST)
- Data source: chat interactions only.
- Pages: Analytics Dashboard, Conversations, Fraud, Sentiment, Escalations, KPI.
- Analytics Copilot answers from current interaction-derived metrics.

### 3) Data Governance Space (ROLE: DATA_STEWARD)
- Pages: Data Governance, Observability, Evaluation Agent.
- AI Governance Copilot answers from evaluation, observability, governance metrics.
- Focus: responsible AI, data quality, compliance, risk visibility.

## End-to-End Functional Flow

1. User input
2. Privacy Agent masking
3. Fraud Agent
4. Sentiment Agent
5. L0 / L1 decision
6. Retrieval Agent (RAG context)
7. GPT-4o / GPT-4.1 generation
8. Compliance Agent controls
9. Explainability annotation
10. Response display to customer
11. Databricks Lakehouse ingestion (Bronze/Silver/Gold target)
12. Analytics and Governance consumption
13. Observability and Evaluation metrics

## Frontend Modular Layout

- ui/app.py: role router and page bootstrapping.
- ui/modules/constants.py: roles and page contracts.
- ui/modules/data_store.py: interaction persistence and normalization.
- ui/modules/shell.py: global shell (header, disclaimer, style loading).
- ui/modules/spaces.py: Customer, Analytics, Governance space renderers.
- ui/modules/copilots.py: Analytics Copilot and AI Governance Copilot logic.
- ui/aelon.css: reusable visual design system.

## Security and Privacy Rules

- Only masked user content is displayed, sent to agents, and persisted.
- PII categories prioritized: phone, email, IBAN, account, card, identity.
- Compliance and explainability metadata captured for supervision.

## LLMOps & Observability Signals

- Relevance Score
- Faithfulness Score
- Hallucination Rate
- Compliance Score
- Answer Quality
- Response time
- Escalation volume

## Scalability Strategy

- Keep renderers stateless and data-driven.
- Add backend API contracts for copilots when moving beyond heuristic mode.
- Introduce feature flags per role/page.
- Add tests per module and per role-based navigation contract.
