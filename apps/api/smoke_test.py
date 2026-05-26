import asyncio
import uuid
from apps.api.app.db.database import get_db, AsyncSessionLocal
from apps.api.app.db.models.core import User, Workspace, WorkspaceMember, RoleEnum
from apps.api.app.db.models.agents import Agent
from sqlalchemy import select
from apps.api.app.services.workspace import initialize_workspace_resources

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

        member = WorkspaceMember(workspace_id=ws.id, user_id=user.id, role=RoleEnum.owner)
        db.add(member)
        await db.commit()
        
        # 3. Coordinator Seeded
        await initialize_workspace_resources(db, ws.id, user.id)
        
        result = await db.execute(select(Agent).where(Agent.workspace_id == ws.id, Agent.is_coordinator == True))
        coordinator = result.scalar_one_or_none()
        if coordinator:
            print(f"✅ Coordinator Seeded: {coordinator.name} (ID: {coordinator.id})")
        else:
            print("❌ Coordinator was not seeded!")
            return
            
        print("🎉 Smoke test completed successfully!")

if __name__ == "__main__":
    asyncio.run(run_smoke_test())
