# AELON

Plateforme bancaire orientee Data + IA, construite sur Databricks, pour ingerer, traiter, ordonner et exploiter des contenus documentaires et conversationnels afin d'alimenter un assistant RAG, des KPI metier, des tableaux de bord Analytics et des controles de Governance.

## Objectif produit

AELON ne se limite pas a un chat. Le coeur de la plateforme est une chaine de valeur data centree sur Databricks :

- ingestion de sources documentaires bancaires
- structuration via architecture medaillon
- preparation des chunks et embeddings
- exposition via Vector Search
- consommation par le moteur RAG pour generer les reponses
- persistance des conversations pour l'analytics, la gouvernance et l'amelioration continue

## Architecture cible

```text
Sources documentaires
-> Bronze
-> Silver
-> Gold
-> Chunking / Embeddings
-> Databricks Vector Search
-> Retrieval Agent
-> Orchestrator IA
-> Chat / APIs
-> gold_conversations
-> Analytics Metrics / Governance Metrics
-> Dashboards / Supervision
```

## Architecture medaillon Databricks

### Bronze

Couche d'atterrissage des sources brutes. Elle conserve les documents collectes avec une logique de tracabilite et de reprise.

Exemples de contenus :

- FAQ bancaires
- contenus ACPR
- contenus Banque de France
- contenus CNIL / FBF
- documents PDF et sources textuelles

### Silver

Couche de normalisation et de nettoyage. Les documents y sont harmonises, dedoublonnes, nettoyes et prepares pour la suite du pipeline.

Objectifs :

- standardiser les structures de donnees
- isoler les contenus utiles au RAG
- supprimer le bruit documentaire
- faciliter la qualite et la gouvernance de la donnee

### Gold

Couche de consommation metier et IA. Elle contient les actifs directement exploitables par les composants applicatifs et analytiques.

Tables principales :

- `fr_raise.rag_pipeline.bronze_documents`
- `fr_raise.rag_pipeline.silver_documents`
- `fr_raise.rag_pipeline.gold_documents`
- `fr_raise.rag_pipeline.gold_embeddings`
- `fr_raise.rag_pipeline.gold_conversations`
- `fr_raise.rag_pipeline.gold_governance`

Tables KPI :

- `fr_raise.rag_pipeline.analytics_metrics`
- `fr_raise.rag_pipeline.governance_metrics`

## Chaine RAG

Le RAG AELON s'appuie sur Databricks comme socle de preparation et de restitution du contexte.

### Etapes principales

1. ingestion des documents dans la medallion architecture
2. generation des chunks documentaires
3. calcul des embeddings avec `databricks-gte-large-en`
4. indexation dans Databricks Vector Search
5. recherche des top chunks par le Retrieval Agent
6. injection du contexte dans l'Orchestrator
7. generation de la reponse par le LLM
8. persistance de la conversation pour reusage analytique et gouvernance

### Flux d'execution

```text
Utilisateur
-> Orchestrator
-> Retrieval Agent
-> Databricks Vector Search
-> Top Chunks
-> LLM
-> Reponse
-> Conversation Logger
-> gold_conversations
```

## Couches IA et usages

### Chat bancaire

Le chat consomme le contexte RAG pour fournir des reponses alimentees par la base documentaire. Les agents de privacy, fraude, sentiment, compliance, explainability et evaluation enrichissent le traitement.

### Analytics

La couche Analytics exploite les conversations sauvegardees pour produire des KPI de pilotage :

- volume de conversations
- questions par jour
- questions par categorie
- sources les plus utilisees
- nombre moyen de chunks recuperes
- temps moyen de reponse
- top requetes utilisateurs

### Governance

La couche Governance suit la qualite et la robustesse du systeme RAG :

- taux de retrieval reussi
- taux de retrieval vide
- nombre de reponses avec sources
- nombre moyen de documents recuperes
- contexte moyen injecte
- citations par source
- signaux d'observabilite et de compliance

## Persistance des conversations

Chaque reponse generee est enregistree dans `fr_raise.rag_pipeline.gold_conversations` avec les attributs suivants :

- `conversation_id`
- `timestamp`
- `question`
- `answer`
- `sources`
- `categories`
- `retrieval_count`
- `response_time_ms`
- `user_session_id`

Cette table devient la source de verite pour :

- l'analyse des usages
- les dashboards metiers
- le suivi de performance du RAG
- l'audit et la gouvernance

Si le SQL Warehouse Databricks est indisponible, les evenements sont stockes temporairement dans :

- `data/processed/failed_conversation_events.jsonl`

Le rejeu est disponible via :

```powershell
Set-Location C:/Users/csileuka/OneDrive - Capgemini/Bureau/PROJETS/AI.Agent.AELON/GEN.AI
.\.venv\Scripts\python.exe .\scripts\replay_failed_conversations.py
```

## APIs principales

### Surface applicative

- `POST /web/chat`
- `GET /dashboards/analytics`
- `GET /dashboards/governance`

### APIs KPI

- `GET /analytics`
- `GET /governance`

Ces endpoints exposent les indicateurs consolides issus des tables Databricks de metrics, avec fallback local si les tables ne sont pas encore materialisees.

## Artefacts Data / KPI

### Scripts SQL

- `sql/analytics_metrics.sql`
- `sql/governance_metrics.sql`
- `sql/analytics_kpis.sql`
- `sql/governance_kpis.sql`

### Notebooks Databricks

- `notebooks/05_analytics_metrics.ipynb`
- `notebooks/06_governance_metrics.ipynb`

## Variables d'environnement critiques

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

Sans `DATABRICKS_SQL_WAREHOUSE_ID`, l'ecriture directe dans `gold_conversations` n'est pas possible et le systeme bascule sur le fichier de reprise local.

## Monitoring et exploitation

Les logs structurants suivants sont emis pour superviser la chaine RAG :

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

Points de surveillance prioritaires :

- disponibilite du SQL Warehouse
- volume de fichiers de reprise locale
- taux de retrieval vide
- degradation du temps de reponse
- baisse du nombre de sources citees

## Demarrage local

### Bootstrap

```powershell
Set-Location C:/Users/csileuka/OneDrive - Capgemini/Bureau/PROJETS/AI.Agent.AELON/GEN.AI
powershell -ExecutionPolicy Bypass -File .\scripts\bootstrap-ui.ps1
```

### Lancement

```powershell
Set-Location C:/Users/csileuka/OneDrive - Capgemini/Bureau/PROJETS/AI.Agent.AELON/GEN.AI
powershell -ExecutionPolicy Bypass -File .\scripts\run-ui.ps1
```

Ou en execution directe :

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn api.main:app --host 127.0.0.1 --port 8010 --reload
```

L'interface web est exposee sur `http://127.0.0.1:8010/`.

## Positionnement AELON

AELON doit etre lu comme une plateforme complete :

- Databricks porte l'ingestion, le traitement et l'ordonnancement des donnees
- la couche RAG se branche sur cette fondation pour alimenter les reponses
- la persistance des conversations alimente l'analytics et la governance
- la couche IA n'est pas isolee : elle repose sur une base data industrialisee, traçable et exploitable