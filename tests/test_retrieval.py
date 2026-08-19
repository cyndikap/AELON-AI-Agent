import os
from dotenv import load_dotenv
from databricks.vector_search.client import VectorSearchClient

load_dotenv()

client = VectorSearchClient(
    workspace_url=os.getenv("DATABRICKS_HOST"),
    personal_access_token=os.getenv("DATABRICKS_TOKEN")
)

index = client.get_index(
    endpoint_name="aelon_vs_endpoint",
    index_name="fr_raise.rag_pipeline.gold_embeddings_index"
)

results = index.similarity_search(
    query_text="Comment signaler une fraude bancaire ?",
    columns=[
        "chunk_id",
        "texte_chunk",
        "categorie",
        "source_document"
    ],
    num_results=5
)

print(results)