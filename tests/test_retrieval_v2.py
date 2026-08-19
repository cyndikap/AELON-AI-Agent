import os
from dotenv import load_dotenv

import mlflow.deployments
from databricks.vector_search.client import VectorSearchClient

load_dotenv()

EMBEDDING_MODEL = "databricks-gte-large-en"

# Client Embedding
deploy_client = mlflow.deployments.get_deploy_client("databricks")

# Client Vector Search
vs_client = VectorSearchClient(
    workspace_url=os.getenv("DATABRICKS_HOST"),
    personal_access_token=os.getenv("DATABRICKS_TOKEN")
)

# Récupération de l'index
index = vs_client.get_index(
    endpoint_name="aelon_vs_endpoint",
    index_name="fr_raise.rag_pipeline.gold_embeddings_index"
)

question = "Comment signaler une fraude bancaire ?"

# Génération embedding question
response = deploy_client.predict(
    endpoint=EMBEDDING_MODEL,
    inputs={
        "input": [question]
    }
)

question_vector = response.data[0]["embedding"]

print("Dimension :", len(question_vector))

# Recherche vectorielle
results = index.similarity_search(
    query_vector=question_vector,
    columns=[
        "chunk_id",
        "texte_chunk",
        "source_document",
        "categorie"
    ],
    num_results=5
)

print(results)