import uuid
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional

from apps.api.app.db.database import get_db
from apps.api.app.db.models.core import Workspace
from apps.api.app.db.models.agents import Team, TeamMember, Agent
from apps.api.app.api.deps import get_current_workspace, require_permission

router = APIRouter()

class TeamCreate(BaseModel):
    name: str
    description: Optional[str] = None
    template: Optional[str] = None

class TeamMemberAdd(BaseModel):
    agent_id: str
    role_in_team: str = "member"

@router.get("")
async def get_teams(
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

@router.post("/{team_id}/members")
async def add_team_member(
    team_id: str,
    member_in: TeamMemberAdd,
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db),
    _ = Depends(require_permission("manage_teams"))
):
    team = await db.get(Team, uuid.UUID(team_id))
    if not team or team.workspace_id != workspace.id:
        raise HTTPException(status_code=404, detail="Team not found")
        
    agent = await db.get(Agent, uuid.UUID(member_in.agent_id))
    if not agent or agent.workspace_id != workspace.id:
        raise HTTPException(status_code=404, detail="Agent not found")
        
    member = TeamMember(
        team_id=team.id,
        agent_id=agent.id,
        role_in_team=member_in.role_in_team
    )
    db.add(member)
    
    # Also update agent's team_id for backward compatibility
    agent.team_id = team.id
    
    await db.commit()
    return {"status": "success"}

@router.delete("/{team_id}/members/{agent_id}")
async def remove_team_member(
    team_id: str,
    agent_id: str,
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db),
    _ = Depends(require_permission("manage_teams"))
):
    team = await db.get(Team, uuid.UUID(team_id))
    if not team or team.workspace_id != workspace.id:
        raise HTTPException(status_code=404, detail="Team not found")
        
    result = await db.execute(
        select(TeamMember)
        .where(TeamMember.team_id == team.id, TeamMember.agent_id == uuid.UUID(agent_id))
    )
    member = result.scalar_one_or_none()
    
    if member:
        await db.delete(member)
        
    agent = await db.get(Agent, uuid.UUID(agent_id))
    if agent and agent.team_id == team.id:
        agent.team_id = None
        
    await db.commit()
    return {"status": "success"}
