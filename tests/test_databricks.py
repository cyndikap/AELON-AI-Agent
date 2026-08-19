import os
from databricks.sdk import WorkspaceClient
from dotenv import load_dotenv

load_dotenv()

print("Début test...")

w = WorkspaceClient(
    host=os.getenv("DATABRICKS_HOST"),
    token=os.getenv("DATABRICKS_TOKEN")
)

me = w.current_user.me()

print("Utilisateur :", me.user_name)