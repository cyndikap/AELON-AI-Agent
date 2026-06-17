# auth.py
# auth.py
import os
from dotenv import load_dotenv
load_dotenv()
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

# Load from env variable
ENV_TOKEN = os.getenv("MCP_TOKEN")

if ENV_TOKEN is None:
    raise RuntimeError(
        "Environment variable MCP_TOKEN is not set. "
        "Please export MCP_TOKEN before starting the server."
    )

VALID_TOKENS = {ENV_TOKEN}

def authenticate(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    if token not in VALID_TOKENS:
        raise HTTPException(status_code=401, detail="Invalid or missing authentication token")
    return True