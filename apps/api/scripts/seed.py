import asyncio
import uuid
import sys
import os

# Ensure apps module is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from apps.api.app.db.database import AsyncSessionLocal
from apps.api.app.db.models.core import Workspace, User

async def seed():
    async with AsyncSessionLocal() as db:
        # Create user
        user = User(
            email="admin@pixos.ai",
            name="Admin User"
        )
        db.add(user)
        
        # We need a fixed UUID for the workspace so the frontend can hardcode it for MVP
        fixed_uuid = uuid.UUID("00000000-0000-0000-0000-000000000000")
        
        # Check if exists
        existing_ws = await db.get(Workspace, fixed_uuid)
        if not existing_ws:
            ws = Workspace(
                id=fixed_uuid,
                name="Test Workspace"
            )
            db.add(ws)
            print(f"Created Workspace with ID: {fixed_uuid}")
        else:
            print(f"Workspace with ID {fixed_uuid} already exists.")
            
        await db.commit()
        print("Seeding complete.")

if __name__ == "__main__":
    asyncio.run(seed())
