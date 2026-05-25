import asyncio
import uuid
import sys
import os

# Ensure apps module is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from apps.api.app.db.database import AsyncSessionLocal
from apps.api.app.db.models.policy import ToolPolicy
from apps.api.app.db.models.billing import CreditBalance
from apps.api.app.db.models.agents import Agent
from sqlalchemy import select
from apps.api.app.services.workspace import initialize_workspace_resources
from apps.api.app.db.models.core import Workspace, User

async def seed():
    async with AsyncSessionLocal() as db:
        # Create user
        # Try to get existing user
        result = await db.execute(select(User).where(User.email == "admin@pixos.ai"))
        existing_user = result.scalar_one_or_none()
        
        if not existing_user:
            user = User(
                email="admin@pixos.ai",
                name="Admin User"
            )
            db.add(user)
            print("Created admin user")
        else:
            print("Admin user already exists")
            
        fixed_uuid = uuid.UUID("00000000-0000-0000-0000-000000000000")
        
        # Check if workspace exists
        existing_ws = await db.get(Workspace, fixed_uuid)
        if not existing_ws:
            ws = Workspace(
                id=fixed_uuid,
                name="Test Workspace"
            )
            db.add(ws)
            await db.commit()
            print(f"Created Workspace with ID: {fixed_uuid}")
            
            # Initialize resources for the workspace
            # user is either newly created or existing
            current_user = user if not existing_user else existing_user
            await initialize_workspace_resources(db, fixed_uuid, current_user.id)
            print("Initialized workspace resources")
        else:
            ws = existing_ws
            print(f"Workspace with ID {fixed_uuid} already exists.")
            
        # 5. Check / Create Credit Balance
        result = await db.execute(select(CreditBalance).filter_by(workspace_id=ws.id))
        cb = result.scalars().first()
        if not cb:
            cb = CreditBalance(workspace_id=ws.id, balance=100000)
            db.add(cb)
            await db.commit()
            print("Seeded Default Credit Balance: 100,000 credits")

        print("Seeding completed successfully.")

if __name__ == "__main__":
    asyncio.run(seed())
