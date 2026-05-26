from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from pydantic import BaseModel
import uuid

from apps.api.app.db.database import get_db
from apps.api.app.db.models.core import Workspace
from apps.api.app.db.models.integrations import IntegrationConnection
from apps.api.app.api.deps import get_current_workspace, require_permission

router = APIRouter()

class IntegrationResponse(BaseModel):
    id: str
    provider: str
    status: str
    created_at: str

class ConnectIntegrationRequest(BaseModel):
    provider: str
    token: str

@router.get("", response_model=List[IntegrationResponse])
async def get_integrations(
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(IntegrationConnection).where(IntegrationConnection.workspace_id == workspace.id)
    )
    connections = result.scalars().all()
    
    return [
        IntegrationResponse(
            id=str(c.id),
            provider=c.provider,
            status=c.status,
            created_at=c.created_at.isoformat() if c.created_at else ""
        ) for c in connections
    ]

@router.post("", response_model=IntegrationResponse)
async def connect_integration(
    req: ConnectIntegrationRequest,
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db),
    _ = Depends(require_permission("manage_integrations"))
):
    # Check if already connected
    result = await db.execute(
        select(IntegrationConnection).where(
            IntegrationConnection.workspace_id == workspace.id,
            IntegrationConnection.provider == req.provider
        )
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        existing.status = "connected"
        existing.encrypted_token = req.token # In a real system, encrypt this properly
        await db.commit()
        await db.refresh(existing)
        connection = existing
    else:
        connection = IntegrationConnection(
            workspace_id=workspace.id,
            provider=req.provider,
            status="connected",
            encrypted_token=req.token # In a real system, encrypt this properly
        )
        db.add(connection)
        await db.commit()
        await db.refresh(connection)
        
    return IntegrationResponse(
        id=str(connection.id),
        provider=connection.provider,
        status=connection.status,
        created_at=connection.created_at.isoformat() if connection.created_at else ""
    )

@router.delete("/{integration_id}")
async def disconnect_integration(
    integration_id: str,
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db),
    _ = Depends(require_permission("manage_integrations"))
):
    try:
        iid = uuid.UUID(integration_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ID")
        
    connection = await db.get(IntegrationConnection, iid)
    if not connection or connection.workspace_id != workspace.id:
        raise HTTPException(status_code=404, detail="Integration not found")
        
    await db.delete(connection)
    await db.commit()
    
    return {"status": "success"}
