import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from datetime import datetime

from apps.api.app.db.database import get_db
from apps.api.app.db.models.core import User, Workspace
from apps.api.app.db.models.integrations import IntegrationConnection
from apps.api.app.api.deps import get_current_workspace, get_current_user
from apps.api.app.core.security import encrypt_token

router = APIRouter()

# Note: In a real app, these would come from settings and be validated
OAUTH_PROVIDERS = {
    "google": {
        "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "scopes": ["https://www.googleapis.com/auth/gmail.modify", "https://www.googleapis.com/auth/calendar"],
    },
    "github": {
        "auth_url": "https://github.com/login/oauth/authorize",
        "token_url": "https://github.com/login/oauth/access_token",
        "scopes": ["repo", "user"],
    },
    "slack": {
        "auth_url": "https://slack.com/oauth/v2/authorize",
        "token_url": "https://slack.com/api/oauth.v2.access",
        "scopes": ["chat:write", "channels:read"],
    }
}

@router.get("/authorize/{provider}")
async def authorize(
    provider: str,
    workspace: Workspace = Depends(get_current_workspace)
):
    if provider not in OAUTH_PROVIDERS:
        raise HTTPException(status_code=400, detail="Unsupported provider")
        
    config = OAUTH_PROVIDERS[provider]
    # Provide a mock URL for the frontend to redirect to.
    # In a real app, you would append client_id, redirect_uri, response_type=code, scope, state
    state = str(workspace.id) # Passing workspace_id as state to recover it in callback
    scopes = " ".join(config["scopes"])
    
    mock_auth_url = f"{config['auth_url']}?client_id=MOCK_CLIENT_ID&redirect_uri=MOCK_REDIRECT&response_type=code&scope={scopes}&state={state}"
    
    return {"url": mock_auth_url}

@router.get("/callback")
async def oauth_callback(
    code: str,
    state: str,
    provider: str = Query(..., description="Provider name e.g. google, github"),
    db: AsyncSession = Depends(get_db)
):
    """
    Callback for the OAuth flow.
    The 'state' parameter contains the workspace_id.
    """
    if provider not in OAUTH_PROVIDERS:
        raise HTTPException(status_code=400, detail="Unsupported provider")
        
    try:
        workspace_id = uuid.UUID(state)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid state parameter")
        
    # In a real app, we would exchange `code` for an access_token via HTTP POST to token_url.
    # For now, we mock the exchange.
    mock_access_token = f"mock_access_token_for_{provider}_{uuid.uuid4().hex[:8]}"
    mock_refresh_token = f"mock_refresh_token_for_{provider}_{uuid.uuid4().hex[:8]}"
    
    # Encrypt the tokens before saving!
    enc_access = encrypt_token(mock_access_token)
    enc_refresh = encrypt_token(mock_refresh_token)
    
    # Check if connection already exists
    result = await db.execute(
        select(IntegrationConnection).where(
            IntegrationConnection.workspace_id == workspace_id,
            IntegrationConnection.provider == provider
        )
    )
    connection = result.scalar_one_or_none()
    
    if connection:
        connection.encrypted_token = enc_access
        connection.refresh_token = enc_refresh
        connection.status = "connected"
        connection.account_email = "mock_user@example.com"
        connection.scopes = OAUTH_PROVIDERS[provider]["scopes"]
    else:
        connection = IntegrationConnection(
            workspace_id=workspace_id,
            provider=provider,
            encrypted_token=enc_access,
            refresh_token=enc_refresh,
            status="connected",
            account_email="mock_user@example.com",
            scopes=OAUTH_PROVIDERS[provider]["scopes"]
        )
        db.add(connection)
        
    await db.commit()
    
    return {"status": "success", "message": f"Successfully connected to {provider}."}
