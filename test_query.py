import asyncio
from apps.api.app.db.database import AsyncSessionLocal
from apps.api.app.db.models.core import User, Workspace, WorkspaceMember
from sqlalchemy import select

async def check():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).limit(1))
        user = result.scalar_one_or_none()
        if not user:
            print("No user")
            return
            
        print("User ID:", user.id)
        
        q = (
            select(Workspace)
            .join(WorkspaceMember, WorkspaceMember.workspace_id == Workspace.id)
            .where(WorkspaceMember.user_id == user.id)
            .order_by(Workspace.created_at)
            .limit(1)
        )
        print("Query:", q)
        result = await session.execute(q)
        ws = result.scalar_one_or_none()
        print("Resolved Workspace:", ws.id if ws else None)

asyncio.run(check())
