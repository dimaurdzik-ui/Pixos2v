import asyncio
import uuid
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from apps.api.app.db.database import AsyncSessionLocal
from apps.api.app.db.models.core import Workspace, User
from apps.api.app.db.models.workflow import Task, WorkflowRun, WorkflowStep, WorkflowEvent
from apps.api.app.workflows.coordinator import coordinator_app

async def test():
    async with AsyncSessionLocal() as db:
        # 1. Fetch seed user and workspace
        fixed_uuid = uuid.UUID("00000000-0000-0000-0000-000000000000")
        ws = await db.get(Workspace, fixed_uuid)
        if not ws:
            print("Run seed.py first.")
            return
            
        # 2. Create Task
        task = Task(
            workspace_id=ws.id,
            description="Smoke test task"
        )
        db.add(task)
        await db.flush()
        
        # 3. Create Workflow Run
        run = WorkflowRun(
            workspace_id=ws.id,
            task_id=task.id
        )
        db.add(run)
        await db.commit()
        
        # 4. Invoke the workflow
        initial_state = {
            "workflow_run_id": str(run.id),
            "task_id": str(task.id),
            "workspace_id": str(ws.id),
            "user_id": str(ws.id), # mock user_id
            "coordinator_agent_id": "11111111-1111-1111-1111-111111111111",
            "current_agent_id": "11111111-1111-1111-1111-111111111111",
            "user_request": task.description,
            "current_step": 0,
            "results": [],
            "tool_calls": []
        }
        
        print("Starting workflow...")
        final_state = await coordinator_app.ainvoke(initial_state)
        print("Workflow completed successfully.")
        
        # 5. Verify WorkflowStep and WorkflowEvent
        from sqlalchemy import select
        steps = (await db.execute(select(WorkflowStep).where(WorkflowStep.workflow_run_id == run.id))).scalars().all()
        events = (await db.execute(select(WorkflowEvent).where(WorkflowEvent.workflow_run_id == run.id))).scalars().all()
        
        print(f"Created {len(steps)} steps.")
        print(f"Created {len(events)} events.")
        
        assert len(steps) > 0, "No steps created!"
        assert len(events) > 0, "No events created!"
        
        print("SMOKE TEST PASSED ✅")

if __name__ == "__main__":
    asyncio.run(test())
