import uuid
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from apps.api.app.db.database import get_db
from apps.api.app.db.models.outputs import Artifact
from apps.api.app.db.models.core import Workspace
from apps.api.app.api.deps import get_current_workspace

router = APIRouter()

@router.get("")
async def list_artifacts(
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Artifact)
        .where(Artifact.workspace_id == workspace.id)
        .order_by(desc(Artifact.created_at))
    )
    artifacts = result.scalars().all()
    
    # Return without full content to save bandwidth
    return [
        {
            "id": str(a.id),
            "name": a.name,
            "artifact_type": a.artifact_type,
            "workflow_run_id": str(a.workflow_run_id) if a.workflow_run_id else None,
            "created_at": a.created_at.isoformat() if a.created_at else None,
            "content_preview": a.content[:100] + "..." if len(a.content) > 100 else a.content
        }
        for a in artifacts
    ]

@router.get("/{artifact_id}")
async def get_artifact(
    artifact_id: str,
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    try:
        aid = uuid.UUID(artifact_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid artifact ID format")
        
    artifact = await db.get(Artifact, aid)
    if not artifact or artifact.workspace_id != workspace.id:
        raise HTTPException(status_code=404, detail="Artifact not found")
        
    return {
        "id": str(artifact.id),
        "name": artifact.name,
        "artifact_type": artifact.artifact_type,
        "content": artifact.content,
        "workflow_run_id": str(artifact.workflow_run_id) if artifact.workflow_run_id else None,
        "created_at": artifact.created_at.isoformat() if artifact.created_at else None
    }
