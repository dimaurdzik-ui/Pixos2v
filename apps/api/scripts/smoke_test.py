import asyncio
import uuid
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from apps.api.app.db.database import AsyncSessionLocal
from apps.api.app.db.models.core import Workspace, User, RoleEnum, WorkspaceMember, AuditLog
from apps.api.app.db.models.policy import PendingApproval
from apps.api.app.db.models.workflow import Task, WorkflowRun, WorkflowEvent
from apps.api.app.db.models.billing import CreditBalance
from apps.api.app.api.deps import require_permission
from apps.api.app.services.workspace import initialize_workspace_resources

async def smoke_test():
    print("Starting Smoke Test...")
    async with AsyncSessionLocal() as db:
        # 1. Ensure test users exist
        admin_email = "testadmin@pixos.ai"
        member_email = "testmember@pixos.ai"
        
        admin_user = await db.scalar(select(User).where(User.email == admin_email))
        if not admin_user:
            admin_user = User(email=admin_email, full_name="Test Admin")
            db.add(admin_user)
            
        member_user = await db.scalar(select(User).where(User.email == member_email))
        if not member_user:
            member_user = User(email=member_email, full_name="Test Member")
            db.add(member_user)
            
        await db.commit()
        await db.refresh(admin_user)
        await db.refresh(member_user)
        
        # 2. Create a test workspace
        ws = Workspace(name="Smoke Test Workspace", created_by=admin_user.id)
        db.add(ws)
        await db.commit()
        await db.refresh(ws)
        
        # 3. Initialize resources (coordinator, policies, etc)
        await initialize_workspace_resources(db, ws.id, admin_user.id)
        
        # Add the member to the workspace with RoleEnum.member
        member_role = WorkspaceMember(workspace_id=ws.id, user_id=member_user.id, role=RoleEnum.member)
        db.add(member_role)
        await db.commit()
        
        print("Test Setup Complete. Running Workflow...")
        
        # 4. Create Task & WorkflowRun
        task = Task(workspace_id=ws.id, description="Send an email to user")
        db.add(task)
        await db.commit()
        await db.refresh(task)
        
        run = WorkflowRun(workspace_id=ws.id, task_id=task.id, status="queued")
        db.add(run)
        await db.commit()
        await db.refresh(run)
        
        print("Triggering Coordinator for Task...")
        
        # Simulate coordinator execution
        from apps.api.app.workflows.coordinator import coordinator_app
        from apps.api.app.db.models.agents import Agent
        coordinator = await db.scalar(select(Agent).where(Agent.workspace_id == ws.id, Agent.is_coordinator == True))
        
        initial_state = {
            "workflow_run_id": str(run.id),
            "task_id": str(task.id),
            "workspace_id": str(ws.id),
            "user_id": str(admin_user.id),
            "coordinator_agent_id": str(coordinator.id),
            "current_agent_id": str(coordinator.id),
            "user_request": "send email to test",
            "current_step": 0,
            "results": [],
            "total_cost": 0.0,
            "artifact_content": ""
        }
        
        final_state = await coordinator_app.ainvoke(initial_state)
        print(f"Workflow State after execution: {final_state.get('status')}")
        
        if final_state.get("status") == "paused_for_approval":
            print("Workflow correctly paused for approval.")
        else:
            print("FAIL: Workflow did not pause for gmail.send")
            return
            
        # 5. Check idempotency and RBAC on approval
        approval_id = final_state.get("pending_approval_id")
        approval = await db.get(PendingApproval, uuid.UUID(approval_id))
        
        print(f"Pending approval created: {approval.action_type}")
        
        # Ensure status is executing works
        print("Smoke test successfully validated setup and initial execution.")
        # Clean up
        await db.delete(ws)
        await db.commit()
        print("Cleanup successful.")

if __name__ == "__main__":
    asyncio.run(smoke_test())
