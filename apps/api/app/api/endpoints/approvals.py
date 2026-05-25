import uuid
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from apps.api.app.db.database import get_db
from apps.api.app.db.models.policy import PendingApproval
from apps.api.app.db.models.core import Workspace, AuditLog
from apps.api.app.api.deps import get_current_workspace
from apps.api.app.db.models.workflow import WorkflowEvent

router = APIRouter()

@router.get("")
async def get_approvals(
    workspace_id: str = Header(...),
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(PendingApproval).where(
            PendingApproval.workspace_id == workspace.id,
            PendingApproval.status == "pending"
        )
    )
    return result.scalars().all()

@router.post("/{approval_id}/approve")
async def approve_tool(
    approval_id: str,
    workspace_id: str = Header(...),
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    approval = await db.get(PendingApproval, uuid.UUID(approval_id))
    if not approval or approval.workspace_id != workspace.id:
        raise HTTPException(status_code=404, detail="Approval not found")
        
    if approval.status != "pending":
        return {"status": approval.status, "message": "Approval already processed"}
        
    approval.status = "approved"
    
    # Execute the tool
    from apps.api.app.services.tools.gateway import ToolGateway
    
    try:
        tool_result = await ToolGateway.execute(approval.action_type, approval.payload_preview or {})
    except Exception as e:
        tool_result = f"Error executing tool: {str(e)}"
        
    # Log event
    event = WorkflowEvent(
        workflow_run_id=approval.workflow_run_id,
        event_type="tool_approved_and_executed",
        payload={"tool": approval.action_type, "result": tool_result}
    )
    db.add(event)
    
    await db.commit()
    return {"status": "approved", "result": tool_result}

@router.post("/{approval_id}/reject")
async def reject_tool(
    approval_id: str,
    workspace_id: str = Header(...),
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    approval = await db.get(PendingApproval, uuid.UUID(approval_id))
    if not approval or approval.workspace_id != workspace.id:
        raise HTTPException(status_code=404, detail="Approval not found")
        
    if approval.status != "pending":
        return {"status": approval.status, "message": "Approval already processed"}
        
    approval.status = "rejected"
    
    event = WorkflowEvent(
        workflow_run_id=approval.workflow_run_id,
        event_type="tool_rejected",
        payload={"tool": approval.action_type}
    )
    db.add(event)
    
    await db.commit()
    return {"status": "rejected"}
