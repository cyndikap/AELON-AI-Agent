import os
from dotenv import load_dotenv
from databricks.vector_search.client import VectorSearchClient

load_dotenv()

client = VectorSearchClient(
    workspace_url=os.getenv("DATABRICKS_HOST"),
    personal_access_token=os.getenv("DATABRICKS_TOKEN")
)

endpoint_name = "aelon_vs_endpoint"

indexes = client.list_indexes(endpoint_name)

print(indexes)