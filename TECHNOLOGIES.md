# 📚 Documentation des Technologies - Système GEN.AI

## Vue d'Ensemble
GEN.AI est un système intelligent de support bancaire multi-niveaux utilisant une architecture orchestrée d'agents IA avec intégration cloud Azure, base de données vectorielle et interface utilisateur intuitive.

---

## 🔧 Stack Technologique Complet

### 1. **Langage & Runtime**
- **Python 3.12** — Langage principal du système
- **Environnement virtuel** — Gestion des dépendances avec `requirements.txt`
- **.env Configuration** — Gestion sécurisée des variables d'environnement

---

## 2. 🤖 Intelligence Artificielle & LLM

### Azure OpenAI
- **Service** : Azure OpenAI API
- **Modèles utilisés** :
  - `gpt-4.1-mini` — Déploiement principal pour chat
  - `gpt-4o` — Modèle alternatif haute performance
  - `text-embedding-ada-002` — Embeddings pour RAG
- **Intégration** : Classe `AzureChatLLM` (wrapper personnalisé)
- **Authentification** : Clé API + endpoint Azure
- **Version API** : `2024-02-15-preview`, `2024-06-01`

### Agents Spécialisés
1. **L0Agent** — Résolution au premier niveau (self-service)
2. **L1Agent** — Diagnostic technique avancé (escalade)
3. **FraudAgent** — Détection et scoring de fraude
4. **SentimentAgent** — Analyse du sentiment client
5. **ComplianceAgent** — Vérification de conformité réglementaire

### Architecture Agentic
- **Orchestrator** — Orchestration centrale du flux décisionnel
- **Retrieval Agent** — Recherche et récupération de données (RAG)
- **MCP Client** — Intégration Model Context Protocol
- **L0 Memory** — Mémoire distribuée pour persistance L0

---

## 3. 🗄️ Base de Données & Vector Store

### ChromaDB
- **Type** : Base de données vectorielle in-memory
- **Fichier** : `chroma.sqlite3`
- **Utilisation** :
  - Stockage d'embeddings de documents
  - Recherche sémantique rapide pour RAG
  - Indexation des réponses fréquentes
- **Intégration** : `load_to_chroma()` dans ETL

### Azure AI Search
- **Service** : Moteur de recherche cloud
- **Index** : `index-savbancaire-da`
- **Utilisation** :
  - Recherche vectorielle hybride (dense + sparse)
  - Knowledge base documents
- **Endpoints** :
  - Recherche : `azure-aisearch-da`
  - Authentification : Clé API Azure

### PostgreSQL/Delta Lake (Optionnel)
- **Utilisation** : Stockage de logs transformés
- **Intégration** : `load_to_delta()` disponible en pipeline

---

## 4. 📊 Traitement de Données & ETL

### Pandas
- **Utilisation** :
  - Manipulation et transformation de DataFrames
  - Agrégations pour analytics dashboard
  - Conversion CSV → JSON

### NumPy
- **Utilisation** :
  - Calculs numériques
  - Opérations vectorisées sur scores de fraude

### Pipeline ETL
```
Extract → Transform → Load (JSON/Chroma/Delta)
├── Extract : données CSV brutes (transactions, fraude, logs)
├── Transform : nettoyage, normalisation, enrichissement
└── Load : 3 destinations parallèles
```

### Fichiers de Données
- **Entrée** : `data/raw/` (CSV)
  - `bank_transactions_data_2.csv`
  - `fraud_data.csv`
  - `sample_logs.csv`
- **Sortie** : `data/processed/logs_clean.json`

---

## 5. 🌐 API & Communication

### FastAPI
- **Framework** : Serveur Web REST asynchrone
- **Port** : À configurer
- **Endpoints** :
  - `POST /query` — Traitement requête utilisateur
  - `GET /logs` — Récupération logs
  - `POST /incidents` — Gestion incidents
- **Authentification** : Fonction `authenticate()` personnalisée
- **Uvicorn** : Serveur ASGI pour FastAPI

### Schemas Pydantic
- `UserQueryRequest` — Input utilisateur
- `AgentResponse` — Réponse formatée agent
- `IncidentRequest` — Rapport d'incident
- `LogEntry`, `QueryResponse` — Modèles de données

### Requests Library
- **Utilisation** : Requêtes HTTP vers services externes
- **Cas d'usage** : Appels aux APIs Azure, webhooks

---

## 6. 🎨 Interface Utilisateur

### Streamlit
- **Framework** : Application web interactive Python
- **Fichier entrypoint** : `ui/app.py`
- **Fonctionnalités** :
  - Chat conversationnel (Mode Utilisateur)
  - Dashboard analytique (Mode Admin)
  - Visualisation en temps réel
  - Thème sombre personnalisé
- **Composants Streamlit** :
  - `st.chat_message()` — Messages conversationnels
  - `st.metric()` — KPIs
  - `st.bar_chart()`, `st.dataframe()` — Visualisations
  - `st.expander()` — Sections repliables
  - `st.session_state` — État persistant

### Styling CSS Personnalisé
- **Gradients** : Blues, purples, teals (inspiré IMG_2155)
- **Composants** :
  - `.dashboard-header` — En-tête admin
  - `.kpi-card` — Cartes métriques
  - `.chart-container` — Conteneurs de graphiques
  - `.section-title` — Titres de sections
  - `.stat-badge` — Badges statistiques
- **Fonts** : Inter (Google Fonts)

---

## 7. 🔐 Sécurité & Configuration

### Python-dotenv
- **Utilisation** : Gestion des secrets
- **Variables clés** :
  - `AZURE_OPENAI_API_KEY`
  - `AZURE_OPENAI_ENDPOINT`
  - `AZURE_AI_SEARCH_API_KEY`
  - `AZURE_OPENAI_CHAT_DEPLOYMENT`

### Authentification
- Fonction personnalisée `authenticate()` en `auth.py`
- Support du middleware FastAPI

### Logging & Monitoring
- Fichiers logs : `data/processed/logs_clean.json`
- Modèle `LogEntry` avec timestamp, severity, service
- Persistence en session Streamlit (`interactions.json`)

---

## 8. 📈 Analytics & Reporting

### Tableau de Bord Admin
- **Visualisations** :
  - Problèmes les plus fréquents (bar chart)
  - Distribution sentiments/urgence (bar charts dual)
  - Niveaux de risque et conformité
  - **Distribution des scores de fraude** ✨ (nouveau)
  - Score moyen de fraude, cas haut/moyen risque
- **Filtres** : Par catégorie, sentiment, agent
- **Dataframe** : 20 dernières interactions

### Metrics Clés
- Interactions totales
- Taux résolution L0 (%)
- Taux escalade L1 (%)
- Fraudes bloquées
- Score fraude moyen
- Cas haut risque (score ≥ 70)
- Taux de conformité

---

## 9. 📁 Structure Modulaire

### Répertoires Principaux
```
GEN.AI/
├── multi_agent/          # Agents orchestrés
│   ├── l0/              # Agent Level-0 (self-service)
│   ├── l1/              # Agent Level-1 (escalade)
│   ├── fraud/           # FraudAgent (scoring)
│   ├── sentiment/       # SentimentAgent
│   ├── compliance/      # ComplianceAgent
│   ├── analytics/       # Analytics agent
│   ├── orchestrator.py  # Orchestration centrale
│   └── main.py          # Test entry point
├── api/                 # Serveur FastAPI
│   ├── main.py
│   ├── schemas.py
│   └── dependencies.py
├── etl/                 # Pipeline ETL
│   ├── extract.py
│   ├── transform.py
│   ├── load.py
│   └── pipeline.py
├── ui/                  # Interface Streamlit
│   ├── app.py          # Application principale
│   └── data/           # Données persistantes
├── knowledge_base/      # Knowledge base IT
│   └── it_support_kb.md
└── data/               # Données brutes & traitées
    ├── raw/
    ├── processed/
    └── chroma/         # Stockage ChromaDB
```

---

## 10. 🔄 Flux d'Architecture Globale

```
Utilisateur (Streamlit UI)
    ↓
Orchestrator
    ├→ FraudAgent (scoring de fraude)
    ├→ SentimentAgent (analyse sentiment)
    ├→ L0Agent (résolution self-service)
    │   └→ Azure KB (recherche)
    │   └→ ChromaDB (RAG)
    ├→ L1Agent (escalade technique)
    │   └→ RetrievalAgent (données Databricks)
    ├→ ComplianceAgent (conformité)
    └→ Response → Streamlit UI
    
Data Pipeline (ETL)
    Extract (CSV) → Transform → Load (Chroma/Delta/JSON)
    
API (FastAPI)
    REST endpoints ← → Orchestrator
```

---

## 11. 📦 Dépendances Principales

| Package | Version | Utilisation |
|---------|---------|-------------|
| **fastapi** | Latest | Serveur API REST |
| **uvicorn** | Latest | ASGI server |
| **streamlit** | Latest | Interface utilisateur |
| **openai** | Latest | Client Azure OpenAI |
| **chromadb** | Latest | Base vectorielle |
| **pandas** | Latest | Manipulation données |
| **numpy** | Latest | Calculs numériques |
| **requests** | Latest | Requêtes HTTP |
| **python-dotenv** | Latest | Config secrets |
| **tiktoken** | Latest | Token counting OpenAI |

---

## 12. 🔧 Configuration Azure

### Services Azure Utilisés
- **Azure OpenAI** — LLM et embeddings
- **Azure Cognitive Search** — Moteur recherche vectoriel
- **Azure Key Vault** (optionnel) — Gestion secrets
- **Databricks** (optionnel) — Data warehouse intégration

### Variables d'Environnement Requises
```env
AZURE_OPENAI_API_KEY=***
AZURE_OPENAI_ENDPOINT=https://assistantsavbancaire.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4.1-mini

AZURE_AI_SEARCH_SERVICE_NAME=azure-aisearch-da
AZURE_AI_SEARCH_INDEX_NAME=index-savbancaire-da
AZURE_AI_SEARCH_API_KEY=***

AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME=text-embedding-ada-002
AZURE_OPENAI_DEPLOYMENT=text-embedding-ada-002
```

---

## 13. 🚀 Points d'Entrée

### Mode Production (API)
```bash
# Lancer le serveur FastAPI
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000
```

### Mode Interface Utilisateur
```bash
# Lancer l'app Streamlit
streamlit run ui/app.py
```

### Mode Test/Orchestration
```bash
# Exécuter test orchestrator
python multi_agent/main.py
```

### Mode ETL
```bash
# Lancer pipeline extraction/transformation
from etl.pipeline import run_pipeline
run_pipeline()
```

---

## 14. ✨ Fonctionnalités Spécialisées

### Détection de Fraude (FraudAgent)
- **Scoring** : 0–100
- **Niveaux de risque** : LOW / MEDIUM / HIGH
- **Raisons détaillées** : Liste des anomalies détectées
- **Patterns** : Mots-clés suspects, montants élevés, urgence

### Analyse de Sentiment (SentimentAgent)
- **Sentiments** : positive, neutral, frustrated, angry
- **Tone hints** : Utilisés pour adapter réponses L0/L1
- **Urgency levels** : low, medium, high

### Vérification de Conformité (ComplianceAgent)
- **Compliance check** : Validation des réponses
- **Risk levels** : LOW, MEDIUM, HIGH
- **Correction** : Rewriting des réponses non conformes

### Knowledge Base Management
- **Format** : Markdown (`it_support_kb.md`)
- **Recherche** : Azure Search + ChromaDB RAG
- **Mémoire L0** : Historique des requêtes/réponses

---

## 15. 📊 Persistence & Data Flow

### Interaction Logging
- **Fichier** : `ui/data/interactions.json`
- **Champs** : timestamp, query, agent, sentiment, urgency, risk_level, fraud_score, compliant
- **Utilisation** : Reconstruction dashboard admin

### L0 Memory
- **Type** : In-memory cache
- **Utilisation** : Accélération recherche
- **Réinitialisation** : À chaque session

### Chroma Vector Store
- **Persistent** : `data/chroma/chroma.sqlite3`
- **Collections** : Documents indexés
- **Similarité** : Cosine distance

---

## 📝 Conclusion

GEN.AI intègre une **stack cloud-native complète** combinant :
- ✅ LLM avancés (Azure OpenAI)
- ✅ Recherche sémantique (ChromaDB + Azure Search)
- ✅ Architecture multi-agent orchestrée
- ✅ API REST scalable (FastAPI)
- ✅ Interface utilisateur responsive (Streamlit)
- ✅ Détection fraude & conformité intégrée
- ✅ Pipeline ETL modulaire
- ✅ Analytics temps réel

**Déploiement** : Cloud-ready sur Azure, extensible pour on-premises.

---

**Dernière mise à jour** : Juin 2026  
**Version** : GEN.AI v1.2 (avec Fraud Scoring & Admin Dashboard redesign)
