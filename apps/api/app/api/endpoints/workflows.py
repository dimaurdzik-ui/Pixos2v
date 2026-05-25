from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
from pydantic import BaseModel
import uuid

from apps.api.app.db.database import get_db
from apps.api.app.db.models.core import Workspace
from apps.api.app.db.models.workflow import Task, WorkflowRun
from apps.api.app.workflows.coordinator import coordinator_app, CoordinatorState

router = APIRouter()

class TaskCreateRequest(BaseModel):
    workspace_id: str
    description: str

@router.post("/tasks")
async def create_task(request: TaskCreateRequest, db: AsyncSession = Depends(get_db)):
    # Validate workspace
    workspace = await db.get(Workspace, uuid.UUID(request.workspace_id))
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
        
    task = Task(
        workspace_id=uuid.UUID(request.workspace_id),
        description=request.description,
        status="pending"
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    
    return {"task_id": str(task.id), "status": task.status}

@router.post("/workflows/{task_id}/run")
async def run_workflow(task_id: str, db: AsyncSession = Depends(get_db)):
    task = await db.get(Task, uuid.UUID(task_id))
    if not task:
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
