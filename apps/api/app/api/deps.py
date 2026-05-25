import uuid
from typing import Optional
from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from apps.api.app.db.database import get_db
from apps.api.app.db.models.core import User, Workspace, WorkspaceMember

# MVP Mock Auth: In production this should validate JWT from Clerk/Auth0
async def get_current_user(
    authorization: str = Header(default="Bearer mock-token-admin"),
    db: AsyncSession = Depends(get_db)
) -> User:
    # Just for MVP: use token to mock user email
    # e.g., "Bearer mock-token-admin" -> admin@pixos.ai
    email = "admin@pixos.ai"
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user

async def get_current_workspace(
    workspace_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Workspace:
    try:
        ws_uuid = uuid.UUID(workspace_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid workspace ID format")

    result = await db.execute(select(Workspace).where(Workspace.id == ws_uuid))
    workspace = result.scalar_one_or_none()
    
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
        
    # TODO: In real implementation, check WorkspaceMember for user_id == current_user.id
    # For now, we allow since seed creates this workspace without explicitly linking members yet
    
    return workspace
