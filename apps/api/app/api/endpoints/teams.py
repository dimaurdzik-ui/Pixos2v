import uuid
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional

from apps.api.app.db.database import get_db
from apps.api.app.db.models.core import Workspace
from apps.api.app.db.models.agents import Team
from apps.api.app.api.deps import get_current_workspace, require_permission

router = APIRouter()

class TeamCreate(BaseModel):
    name: str
    description: Optional[str] = None

@router.get("")
async def get_teams(
    workspace_id: str = Header(...),
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Team).where(Team.workspace_id == workspace.id).order_by(Team.created_at)
    )
    teams = result.scalars().all()
    
    return [
        {
            "id": str(t.id),
            "name": t.name,
            "description": t.description,
            "created_at": t.created_at.isoformat() if t.created_at else None
        }
        for t in teams
    ]

@router.post("", response_model=dict)
async def create_team(
    team_in: TeamCreate,
    workspace_id: str = Header(...),
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db),
    _ = Depends(require_permission("manage_teams"))
):
    new_team = Team(
        workspace_id=workspace.id,
        name=team_in.name,
        description=team_in.description
    )
    db.add(new_team)
    await db.commit()
    await db.refresh(new_team)
    
    return {
        "id": str(new_team.id),
        "name": new_team.name,
        "description": new_team.description
    }

@router.delete("/{team_id}")
async def delete_team(
    team_id: str,
    workspace_id: str = Header(...),
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db),
    _ = Depends(require_permission("manage_teams"))
):
    try:
        tid = uuid.UUID(team_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid team ID")
        
    team = await db.get(Team, tid)
    if not team or team.workspace_id != workspace.id:
        raise HTTPException(status_code=404, detail="Team not found")
        
    await db.delete(team)
    await db.commit()
    return {"status": "success"}
