from fastapi import APIRouter, Depends, HTTPException, Header, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
import uuid
import logging

from apps.api.app.db.database import get_db, AsyncSessionLocal
from apps.api.app.db.models.billing import CreditBalance
from apps.api.app.db.models.core import Workspace, User
from apps.api.app.db.models.agents import Agent
from apps.api.app.db.models.workflow import Task as DBTask, WorkflowRun, WorkflowStep, WorkflowEvent
from apps.api.app.api.deps import get_current_workspace, get_current_user, require_permission
from apps.api.app.workflows.coordinator import coordinator_app

router = APIRouter()
logger = logging.getLogger(__name__)

class TaskCreate(BaseModel):
    description: str

class TaskResponse(BaseModel):
    task_id: str
    workflow_run_id: str
    status: str

async def run_coordinator_background(initial_state: dict):
    try:
        final_state = await coordinator_app.ainvoke(initial_state)
        
        # Deduct credits if completed
        if final_state.get("status") == "completed":
            async with AsyncSessionLocal() as db:
                result = await db.execute(select(CreditBalance).where(CreditBalance.workspace_id == initial_state["workspace_id"]))
                balance = result.scalars().first()
                if balance:
                    balance.balance -= 10
                    from apps.api.app.db.models.billing import UsageRecord
                    usage = UsageRecord(
                        workspace_id=initial_state["workspace_id"],
                        workflow_run_id=initial_state["workflow_run_id"],
                        cost=10
                    )
                    db.add(usage)
                    await db.commit()
                    
    except Exception as e:
        logger.error(f"Coordinator failed: {e}")
        async with AsyncSessionLocal() as db:
            run = await db.get(WorkflowRun, uuid.UUID(initial_state["workflow_run_id"]))
            if run:
                run.status = "failed"
                await db.commit()

@router.post("/tasks", response_model=TaskResponse)
async def create_task(
    task_in: TaskCreate,
    background_tasks: BackgroundTasks,
    workspace: Workspace = Depends(get_current_workspace),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _ = Depends(require_permission("run_workflows"))
):
    # 1. Check Credit Balance
    result = await db.execute(select(CreditBalance).where(CreditBalance.workspace_id == workspace.id))
    balance = result.scalars().first()
    if not balance or balance.balance < 10:
        raise HTTPException(status_code=402, detail="INSUFFICIENT_CREDITS")

    # 2. Create task
    new_task = DBTask(
        workspace_id=workspace.id,
        description=task_in.description,
        status="pending"
    )
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    
    # 2. Create WorkflowRun
    run = WorkflowRun(
        workspace_id=workspace.id,
        task_id=new_task.id,
        status="queued"
    )
    db.add(run)
    await db.commit()
    await db.refresh(run)
    
    # 3. Get coordinator
    result = await db.execute(
        select(Agent).where(Agent.workspace_id == workspace.id, Agent.is_coordinator == True)
    )
    coordinator = result.scalar_one_or_none()
    if not coordinator:
        raise HTTPException(status_code=500, detail="No coordinator agent found for workspace")
        
    initial_state = {
        "workflow_run_id": str(run.id),
        "task_id": str(new_task.id),
        "workspace_id": str(workspace.id),
        "user_id": str(current_user.id),
        "coordinator_agent_id": str(coordinator.id),
        "current_agent_id": str(coordinator.id),
        "user_request": new_task.description,
        "current_step": 0,
        "results": [],
        "total_cost": 0.0,
        "artifact_content": ""
    }
    
    # 4. Trigger background task
    background_tasks.add_task(run_coordinator_background, initial_state)
    
    return {"task_id": str(new_task.id), "workflow_run_id": str(run.id), "status": run.status}

@router.get("")
async def get_workflows(
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    # Fetch runs and their corresponding tasks
    result = await db.execute(
        select(WorkflowRun, DBTask)
        .join(DBTask, WorkflowRun.task_id == DBTask.id)
        .where(WorkflowRun.workspace_id == workspace.id)
        .order_by(WorkflowRun.created_at.desc())
        .limit(20)
    )
    runs = result.all()
    
    return [
        {
            "id": str(run.WorkflowRun.id),
            "task_id": str(run.WorkflowRun.task_id),
            "description": run.Task.description,
            "status": run.WorkflowRun.status,
            "created_at": run.WorkflowRun.created_at.isoformat() if run.WorkflowRun.created_at else None
        }
        for run in runs
    ]

@router.get("/{run_id}")
async def get_workflow_status(
    run_id: str,
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    run = await db.get(WorkflowRun, uuid.UUID(run_id))
    if not run or run.workspace_id != workspace.id:
        raise HTTPException(status_code=404, detail="Workflow run not found")
        
    task = await db.get(DBTask, run.task_id)
    
    # Get steps
    steps_result = await db.execute(
        select(WorkflowStep).where(WorkflowStep.workflow_run_id == run.id).order_by(WorkflowStep.created_at)
    )
    steps = steps_result.scalars().all()
    
    # Get events
    events_result = await db.execute(
        select(WorkflowEvent).where(WorkflowEvent.workflow_run_id == run.id).order_by(WorkflowEvent.created_at)
    )
    events = events_result.scalars().all()
    
    return {
        "id": str(run.id),
        "task_id": str(run.task_id),
        "task_description": task.description if task else "",
        "status": run.status,
        "created_at": run.created_at.isoformat() if run.created_at else None,
        "steps": [{"id": str(s.id), "action": s.action, "status": s.status} for s in steps],
        "events": [{"id": str(e.id), "type": e.event_type, "payload": e.payload} for e in events]
    }
