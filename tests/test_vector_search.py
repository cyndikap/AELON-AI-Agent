import os
from dotenv import load_dotenv
from databricks.vector_search.client import VectorSearchClient

print("1 - Début du script")

load_dotenv()

print("2 - ENV chargé")

host = os.getenv("DATABRICKS_HOST")
token = os.getenv("DATABRICKS_TOKEN")

print("HOST =", host)

client = VectorSearchClient(
    workspace_url=host,
    personal_access_token=token
)

print("3 - Client créé")

try:
    endpoints = client.list_endpoints()
    print("4 - Endpoints récupérés")
    print(endpoints)
except Exception as e:
    print("ERREUR :", e)