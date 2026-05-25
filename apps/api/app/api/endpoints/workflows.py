from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
import uuid

from apps.api.app.db.database import get_db
from apps.api.app.db.models.core import Workspace, User
from apps.api.app.db.models.agents import Agent
from apps.api.app.db.models.workflow import Task as DBTask, WorkflowRun
from apps.api.app.api.deps import get_current_workspace, get_current_user
from apps.api.app.workflows.coordinator import coordinator_app, CoordinatorState

router = APIRouter()

class TaskCreate(BaseModel):
    description: str

@router.post("/tasks")
async def create_task(
    task_in: TaskCreate,
    workspace_id: str = Header(...),
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    new_task = DBTask(
        workspace_id=workspace.id,
        description=task_in.description,
        status="pending"
    )
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    
    return {"task_id": str(new_task.id), "status": new_task.status}

@router.post("/workflows/{task_id}/run")
async def run_workflow(
    task_id: str, 
    workspace_id: str = Header(...),
    workspace: Workspace = Depends(get_current_workspace),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    task = await db.get(DBTask, uuid.UUID(task_id))
    if not task or task.workspace_id != workspace.id:
        raise HTTPException(status_code=404, detail="Task not found")
        
    # Create workflow run
    run = WorkflowRun(
        workspace_id=task.workspace_id,
        task_id=task.id,
        status="started"
    )
    db.add(run)
    await db.commit()
    await db.refresh(run)
    
    # Trigger LangGraph synchronously for testing
    # Fetch the coordinator agent for this workspace
    result = await db.execute(
        select(Agent).where(Agent.workspace_id == workspace.id, Agent.is_coordinator == True)
    )
    coordinator = result.scalar_one_or_none()
    if not coordinator:
        raise HTTPException(status_code=500, detail="No coordinator agent found for workspace")
        
    coordinator_id_str = str(coordinator.id)

    initial_state = {
        "workflow_run_id": str(run.id),
        "task_id": str(task.id),
        "workspace_id": str(task.workspace_id),
        "user_id": str(current_user.id),
        "coordinator_agent_id": coordinator_id_str,
        "current_agent_id": coordinator_id_str,
        "user_request": task.description,
        "current_step": 0,
        "results": [],
        "total_cost": 0.0,
        "artifact_content": ""
    }
    
    # Run the graph
    final_state = await coordinator_app.ainvoke(initial_state)
    
    return {
        "workflow_run_id": str(run.id),
        "results": final_state.get("results"),
        "total_cost": final_state.get("total_cost")
    }
