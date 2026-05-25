import uuid
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional

from apps.api.app.db.database import get_db
from apps.api.app.db.models.agents import Agent
from apps.api.app.db.models.core import Workspace
from apps.api.app.api.deps import get_current_workspace

router = APIRouter()

class AgentCreate(BaseModel):
    name: str
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    model_name: Optional[str] = "gpt-4o"
    temperature: Optional[float] = 0.7

@router.get("")
async def get_agents(
    workspace_id: str = Header(...),
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Agent).where(Agent.workspace_id == workspace.id).order_by(Agent.created_at)
    )
    agents = result.scalars().all()
    
    return [
        {
            "id": str(a.id),
            "name": a.name,
            "description": a.description,
            "is_coordinator": a.is_coordinator,
            "model_name": a.model_name,
            "system_prompt": a.system_prompt,
            "created_at": a.created_at.isoformat() if a.created_at else None
        }
        for a in agents
    ]

@router.post("")
async def create_agent(
    agent_in: AgentCreate,
    workspace_id: str = Header(...),
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    new_agent = Agent(
        workspace_id=workspace.id,
        name=agent_in.name,
        description=agent_in.description,
        system_prompt=agent_in.system_prompt,
        model_name=agent_in.model_name,
        temperature=agent_in.temperature,
        is_coordinator=False
    )
    db.add(new_agent)
    await db.commit()
    await db.refresh(new_agent)
    
    return {
        "id": str(new_agent.id),
        "name": new_agent.name,
        "description": new_agent.description,
        "is_coordinator": new_agent.is_coordinator
    }
