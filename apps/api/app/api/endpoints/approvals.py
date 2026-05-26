import uuid
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from apps.api.app.db.database import get_db
from apps.api.app.db.models.policy import PendingApproval
from apps.api.app.db.models.core import Workspace, AuditLog, User
from apps.api.app.api.deps import get_current_workspace, require_permission, get_current_user
from apps.api.app.db.models.workflow import WorkflowEvent, WorkflowRun
from apps.api.app.core.statuses import ApprovalStatus

router = APIRouter()

@router.get("")
async def get_approvals(
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(PendingApproval).where(
            PendingApproval.workspace_id == workspace.id,
            PendingApproval.status == ApprovalStatus.pending
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
        
    if approval.status != ApprovalStatus.pending:
        return {"status": approval.status, "message": "Approval already processed or executing"}
        
    # Idempotency / Execution Status
    approval.status = ApprovalStatus.executing
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
    
    # Log event
    event = WorkflowEvent(
        workflow_run_id=approval.workflow_run_id,
        event_type="tool_approved",
        payload={"tool": approval.action_type}
    )
    db.add(event)
    
    # Update workflow run status
    run = await db.get(WorkflowRun, approval.workflow_run_id)
    if run:
        run.status = "running"
        
        # Proper LangGraph State Resume
        from apps.api.app.workflows.coordinator import coordinator_app
        from apps.api.app.tasks.worker import run_coordinator_task
        
        config = {"configurable": {"thread_id": str(run.id)}}
        
        # Fetch current state
        current_state_snapshot = await coordinator_app.aget_state(config)
        current_values = current_state_snapshot.values if current_state_snapshot else {}
        
        # We DO NOT execute the tool here! 
        # We simply mark the pending_approval_id as cleared and change status to "running".
        # The LangGraph resume will pick up from the pause node and transition to execute_tools.
        
        try:
            # Update the persisted graph state
            await coordinator_app.aupdate_state(
                config,
                {
                    "status": "running",
                    "pending_approval_id": None
                }
            )
            
            # Dispatch background worker to resume graph
            run_coordinator_task.delay({"workflow_run_id": str(run.id)})
            
        except Exception as e:
            print(f"Error resuming graph: {e}")
            run.status = "failed"
    
    await db.commit()
    return {"status": approval.status, "message": "Approval granted. Execution resuming in background."}

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
        
    if approval.status != ApprovalStatus.pending:
        return {"status": approval.status, "message": "Approval already processed"}
        
    approval.status = ApprovalStatus.rejected
    
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
