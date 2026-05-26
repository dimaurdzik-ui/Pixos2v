import asyncio
import uuid
import os
os.environ["OPENAI_API_KEY"] = ""
from apps.api.app.db.database import get_db, AsyncSessionLocal
from apps.api.app.db.models.core import User, Workspace, WorkspaceMember, RoleEnum
from apps.api.app.db.models.agents import Agent
from sqlalchemy import select
from apps.api.app.services.workspace import initialize_workspace_resources
from apps.api.app.db.models.chat import Conversation, Message
from apps.api.app.db.models.policy import PendingApproval
from apps.api.app.main import app
from httpx import AsyncClient, ASGITransport

async def run_smoke_test():
    print("Starting smoke test...")
    async with AsyncSessionLocal() as db:
        # 1. Mock User Creation
        clerk_id = f"smoke_user_{uuid.uuid4().hex[:8]}"
        email = f"{clerk_id}@test.com"
        
        user = User(clerk_id=clerk_id, email=email, full_name="Smoke Tester")
        db.add(user)
        await db.commit()
        await db.refresh(user)
        print(f"✅ Created User: {user.email} (ID: {user.id})")

        # 2. Workspace Auto-creation
        ws = Workspace(name=f"{user.full_name}'s Workspace", created_by=user.id)
        db.add(ws)
        await db.commit()
        await db.refresh(ws)
        print(f"✅ Created Workspace: {ws.name} (ID: {ws.id})")

        
        # 3. Coordinator Seeded
        await initialize_workspace_resources(db, ws.id, user.id)
        
        result = await db.execute(select(Agent).where(Agent.workspace_id == ws.id, Agent.is_coordinator == True))
        coordinator = result.scalar_one_or_none()
        if coordinator:
            print(f"✅ Coordinator Seeded: {coordinator.name} (ID: {coordinator.id})")
        else:
            print("❌ Coordinator was not seeded!")
            return
            
        print("🎉 Smoke test DB seed completed successfully!")
        
        # Test Endpoints using httpx AsyncClient
        print("\n--- Testing API Endpoints ---")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            headers = {
                "workspace-id": str(ws.id)
            }
            # Override dependency for current_user
            from apps.api.app.api.deps import get_current_user
            app.dependency_overrides[get_current_user] = lambda: user
            
            # 1. Chat with Coordinator
            print(f"Testing Chat with Coordinator {coordinator.id}...")
            chat_payload = {
                "message": "Send an email to test@example.com with subject hello"
            }
            res = await client.post(f"/api/v1/agents/{coordinator.id}/chat", json=chat_payload, headers=headers)
            if res.status_code != 200:
                print(f"❌ Chat endpoint failed: {res.text}")
                return
            chat_data = res.json()
            print(f"✅ Chat response: {chat_data['message']}")
            
            # 2. Check Pending Approval
            print("Checking Pending Approvals...")
            res = await client.get("/api/v1/approvals", headers=headers)
            if res.status_code != 200:
                print(f"❌ Approvals get failed: {res.text}")
                return
            approvals = res.json()
            if not approvals:
                print("❌ No pending approvals created for the email request!")
                return
            
            approval_id = approvals[0]["id"]
            print(f"✅ Found Pending Approval: {approval_id}")
            
            # 3. Execute Approval
            print(f"Executing Approval {approval_id}...")
            res = await client.post(f"/api/v1/approvals/{approval_id}/approve", headers=headers)
            if res.status_code != 200:
                print(f"❌ Approval execution failed: {res.text}")
                return
            exec_data = res.json()
            print(f"✅ Approval Execution Result: {exec_data['result']}")
            
            print("\n🎉 All smoke tests passed successfully!")

if __name__ == "__main__":
    asyncio.run(run_smoke_test())
