import uuid
from typing import Optional
from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from apps.api.app.db.database import get_db
from apps.api.app.db.models.core import User, Workspace, WorkspaceMember

import json
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from apps.api.app.core.config import settings

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    if settings.ENVIRONMENT == "production":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Mock Auth is strictly forbidden in production. Implement real JWT logic."
        )

    token = credentials.credentials
    # For MVP, we use the token directly as the email (e.g. "admin@pixos.ai")
    # In production, replace with:
    # payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    # email = payload.get("email")
    email = token
    
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or invalid token",
        )
    return user

async def get_current_workspace(
    workspace_id: str = Header(..., description="The ID of the workspace"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Workspace:
    try:
        ws_uuid = uuid.UUID(workspace_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid workspace ID format")

    result = await db.execute(
        select(WorkspaceMember)
        .where(
            WorkspaceMember.workspace_id == ws_uuid,
            WorkspaceMember.user_id == current_user.id
        )
    )
    membership = result.scalar_one_or_none()
    
    if not membership:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this workspace")
        
    result_ws = await db.execute(select(Workspace).where(Workspace.id == ws_uuid))
    workspace = result_ws.scalar_one_or_none()
    
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
        
    return workspace

ROLE_PERMISSIONS = {
    "owner": [
        "manage_workspace", "manage_members", "manage_billing", "manage_agents", 
        "manage_teams", "manage_integrations", "run_workflows", "approve_actions", 
        "view_artifacts", "view_audit_logs", "manage_tool_policies"
    ],
    "admin": [
        "manage_agents", "manage_teams", "manage_integrations", "approve_actions",
        "view_artifacts", "view_audit_logs", "run_workflows"
    ],
    "manager": [
        "run_workflows", "approve_actions", "view_artifacts"
    ],
    "member": [
        "run_workflows", "view_artifacts"
    ],
    "viewer": [
        "view_artifacts"
    ]
}

def require_permission(required_permission: str):
    async def permission_checker(
        workspace: Workspace = Depends(get_current_workspace),
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ):
        if current_user.is_super_admin:
            return True
            
        result = await db.execute(
            select(WorkspaceMember)
            .where(
                WorkspaceMember.workspace_id == workspace.id,
                WorkspaceMember.user_id == current_user.id
            )
        )
        membership = result.scalar_one_or_none()
        
        if not membership:
             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a workspace member")
             
        user_role = membership.role.value
        allowed_permissions = ROLE_PERMISSIONS.get(user_role, [])
        
        if required_permission not in allowed_permissions:
             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Requires {required_permission} permission")
             
        return True
    return permission_checker
