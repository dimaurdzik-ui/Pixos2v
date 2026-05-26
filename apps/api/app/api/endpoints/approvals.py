import uuid
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from apps.api.app.db.database import get_db
from apps.api.app.db.models.policy import PendingApproval
from apps.api.app.db.models.core import Workspace, AuditLog, User
from apps.api.app.api.deps import get_current_workspace, require_permission, get_current_user
from apps.api.app.db.models.workflow import WorkflowEvent, WorkflowRun

router = APIRouter()

@router.get("")
async def get_approvals(
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
    workspace: Workspace = Depends(get_current_workspace),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _ = Depends(require_permission("approve_actions"))
):
    approval = await db.get(PendingApproval, uuid.UUID(approval_id))
    if not approval or approval.workspace_id != workspace.id:
        raise HTTPException(status_code=404, detail="Approval not found")
        
    if approval.status != "pending":
        return {"status": approval.status, "message": "Approval already processed or executing"}
        
    # Idempotency / Execution Status
    approval.status = "executing"
    await db.commit() # lock the state
    
    # Audit Log
    audit = AuditLog(
        workspace_id=workspace.id,
        user_id=current_user.id,
        action="approve_tool",
        target_id=str(approval.id),
        details={"tool": approval.action_type}
    )
    db.add(audit)
    
    # Execute the tool
    from apps.api.app.services.tools.gateway import ToolGateway
    
    try:
        context = {
            "workspace_id": str(approval.workspace_id),
            "workflow_run_id": str(approval.workflow_run_id) if approval.workflow_run_id else None
        }
        tool_result = await ToolGateway.execute(approval.action_type, approval.payload_preview or {}, context)
        approval.status = "executed"
    except Exception as e:
        tool_result = f"Error executing tool: {str(e)}"
        approval.status = "failed"
        
    # Log event
    event = WorkflowEvent(
        workflow_run_id=approval.workflow_run_id,
        event_type="tool_approved_and_executed",
        payload={"tool": approval.action_type, "result": tool_result}
    )
    db.add(event)
    
    # Update workflow run status
    run = await db.get(WorkflowRun, approval.workflow_run_id)
    if run:
        # Instead of 'completed', we mark it as running so a background worker could pick it up
        run.status = "running"
    
    await db.commit()
    return {"status": approval.status, "result": tool_result}

@router.post("/{approval_id}/reject")
async def reject_tool(
    approval_id: str,
    workspace: Workspace = Depends(get_current_workspace),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _ = Depends(require_permission("approve_actions"))
):
    approval = await db.get(PendingApproval, uuid.UUID(approval_id))
    if not approval or approval.workspace_id != workspace.id:
        raise HTTPException(status_code=404, detail="Approval not found")
        
    if approval.status != "pending":
        return {"status": approval.status, "message": "Approval already processed"}
        
    approval.status = "rejected"
    
    # Audit Log
    audit = AuditLog(
        workspace_id=workspace.id,
        user_id=current_user.id,
        action="reject_tool",
        target_id=str(approval.id),
        details={"tool": approval.action_type}
    )
    db.add(audit)
    
    event = WorkflowEvent(
        workflow_run_id=approval.workflow_run_id,
        event_type="tool_rejected",
        payload={"tool": approval.action_type}
    )
    db.add(event)
    
    # Update workflow run status
    run = await db.get(WorkflowRun, approval.workflow_run_id)
    if run:
        run.status = "failed"
    
    await db.commit()
    return {"status": "rejected"}
