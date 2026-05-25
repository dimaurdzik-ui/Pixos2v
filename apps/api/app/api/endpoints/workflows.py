from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
import uuid

from apps.api.app.db.database import get_db
from apps.api.app.db.models.core import Workspace
from apps.api.app.db.models.workflow import Task as DBTask, WorkflowRun
from apps.api.app.api.deps import get_current_workspace
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
    initial_state = {
        "workflow_run_id": str(run.id),
        "task_id": str(task.id),
        "workspace_id": str(task.workspace_id),
        "coordinator_agent_id": "11111111-1111-1111-1111-111111111111",
        "current_agent_id": "11111111-1111-1111-1111-111111111111", # same as coordinator
        "user_id": str(workspace.id), # TODO: replace with actual user id from get_current_workspace/user
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
