import os
from dotenv import load_dotenv
load_dotenv()
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer(auto_error=False)

ENV_TOKEN = (os.getenv("MCP_TOKEN") or "").strip()
AUTH_REQUIRED = (os.getenv("MCP_AUTH_REQUIRED") or "false").strip().lower() in {"1", "true", "yes"}
VALID_TOKENS = {ENV_TOKEN} if ENV_TOKEN else set()

def authenticate(credentials: HTTPAuthorizationCredentials | None = Security(security)):
    if not AUTH_REQUIRED and not VALID_TOKENS:
        return True

    if credentials is None:
        raise HTTPException(status_code=401, detail="Missing authentication token")

    token = credentials.credentials
    if token not in VALID_TOKENS:
        raise HTTPException(status_code=401, detail="Invalid or missing authentication token")
    return True