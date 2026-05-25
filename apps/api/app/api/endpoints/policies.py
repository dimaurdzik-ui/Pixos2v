from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List, Optional

from apps.api.app.db.database import get_db
from apps.api.app.db.models.core import Workspace, User
from apps.api.app.db.models.policy import ToolPolicy
from apps.api.app.api.deps import get_current_workspace, get_current_user, require_permission
from apps.api.app.services.tools.registry import ToolRegistry

router = APIRouter()

class PolicyResponse(BaseModel):
    tool_name: str
    description: str
    risk_level: str
    approval_required: str

class PolicyUpdateRequest(BaseModel):
    approval_required: str # "auto", "approval_optional", "approval_required"

@router.get("/", response_model=List[PolicyResponse])
async def list_policies(
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    """List all available tools and their current policies for the workspace"""
    schemas = ToolRegistry._tools
    
    # Get saved policies for this workspace
    result = await db.execute(
        select(ToolPolicy).where(ToolPolicy.workspace_id == workspace.id)
    )
    saved_policies = {p.tool_name: p for p in result.scalars().all()}
    
    policies = []
    for tool_name, tool_def in schemas.items():
        # Use saved policy if exists, otherwise defaults from registry
        if tool_name in saved_policies:
            policy = saved_policies[tool_name]
            approval = policy.approval_required
        else:
            approval = "approval_required" if tool_def.default_risk_level == "HIGH" else "auto"
            
        policies.append(PolicyResponse(
            tool_name=tool_name,
            description=tool_def.description,
            risk_level=tool_def.default_risk_level,
            approval_required=approval
        ))
        
    return policies

@router.put("/{tool_name}", response_model=PolicyResponse)
async def update_policy(
    tool_name: str,
    request: PolicyUpdateRequest,
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db),
    check_perm = Depends(require_permission("manage_tool_policies"))
):
    """Update policy for a specific tool"""
    tool_def = ToolRegistry._tools.get(tool_name)
    if not tool_def:
        raise HTTPException(status_code=404, detail="Tool not found in registry")
        
    if request.approval_required not in ["auto", "approval_optional", "approval_required"]:
        raise HTTPException(status_code=400, detail="Invalid approval_required value")

    result = await db.execute(
        select(ToolPolicy).where(
            ToolPolicy.workspace_id == workspace.id,
            ToolPolicy.tool_name == tool_name
        )
    )
    policy = result.scalar_one_or_none()
    
    if policy:
        policy.approval_required = request.approval_required
    else:
        policy = ToolPolicy(
            workspace_id=workspace.id,
            tool_name=tool_name,
            risk_level=tool_def.default_risk_level,
            approval_required=request.approval_required
        )
        db.add(policy)
        
    await db.commit()
    
    return PolicyResponse(
        tool_name=tool_name,
        description=tool_def.description,
        risk_level=tool_def.default_risk_level,
        approval_required=request.approval_required
    )
