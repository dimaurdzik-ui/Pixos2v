from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
from pydantic import BaseModel
import uuid

from apps.api.app.db.database import get_db
from apps.api.app.db.models.policy import PendingApproval
from apps.api.app.db.models.workflow import WorkflowRun, Task
from apps.api.app.workflows.coordinator import coordinator_app, CoordinatorState
from apps.api.app.db.models.core import AuditLog

from sqlalchemy import select

router = APIRouter()

@router.get("")
async def get_approvals(workspace_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(PendingApproval).where(
            PendingApproval.workspace_id == uuid.UUID(workspace_id),
            PendingApproval.status == "pending"
        )
    )
    approvals = result.scalars().all()
    return [{"id": str(a.id), "tool": a.action_type, "risk": a.risk_level, "payload": a.payload_preview, "status": a.status} for a in approvals]

@router.post("/{approval_id}/approve")
async def approve_action(approval_id: str, db: AsyncSession = Depends(get_db)):
    approval = await db.get(PendingApproval, uuid.UUID(approval_id))
    if not approval or approval.status != "pending":
        raise HTTPException(status_code=404, detail="Pending approval not found or already processed")
        
    approval.status = "approved"
    await db.commit()
    
    # Log Audit
    log = AuditLog(
        workspace_id=approval.workspace_id,
        actor_type="user",
        action="approval_approved",
        resource_type="pending_approval",
        resource_id=str(approval.id),
        metadata_={"tool": approval.action_type}
    )
    db.add(log)
    
    run = await db.get(WorkflowRun, approval.workflow_run_id)
    task = await db.get(Task, run.task_id)
    
    # Resume the workflow run
    # For MVP we re-initialize the state with `pending_approval_id` to skip prior steps
    resume_state = {
        "workflow_run_id": str(run.id),
        "task_id": str(task.id),
        "workspace_id": str(run.workspace_id),
        "user_request": task.description,
        "current_step": 1,
        "results": ["Resumed from approval"],
        "total_cost": 0.0,
        "artifact_content": "",
        "tool_calls": [{"tool": approval.action_type, "payload": approval.payload_preview}],
        "pending_approval_id": str(approval.id),
        "status": "running"
    }
    
    final_state = await coordinator_app.ainvoke(resume_state)
    
    return {"status": "approved_and_resumed", "workflow_results": final_state.get("results")}

@router.post("/{approval_id}/reject")
async def reject_action(approval_id: str, db: AsyncSession = Depends(get_db)):
    approval = await db.get(PendingApproval, uuid.UUID(approval_id))
    if not approval or approval.status != "pending":
        raise HTTPException(status_code=404, detail="Pending approval not found or already processed")
        
    approval.status = "rejected"
    
    # Update run status
    run = await db.get(WorkflowRun, approval.workflow_run_id)
    run.status = "failed"
    
    # Log Audit
    log = AuditLog(
        workspace_id=approval.workspace_id,
        actor_type="user",
        action="approval_rejected",
        resource_type="pending_approval",
        resource_id=str(approval.id)
    )
    db.add(log)
    await db.commit()
    
    return {"status": "rejected", "message": "Workflow run has been stopped."}
