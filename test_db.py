import asyncio
from apps.api.app.db.database import AsyncSessionLocal
from apps.api.app.db.models.core import User, Workspace, WorkspaceMember
from sqlalchemy import select

async def check():
    async with AsyncSessionLocal() as session:
        users = (await session.execute(select(User))).scalars().all()
        print('Users:', len(users))
        for u in users: print(f"  User: {u.email}, ID: {u.id}")
        
        workspaces = (await session.execute(select(Workspace))).scalars().all()
        print('Workspaces:', len(workspaces))
        for w in workspaces: print(f"  Workspace: {w.name}, ID: {w.id}")

        members = (await session.execute(select(WorkspaceMember))).scalars().all()
        print('Members:', len(members))
        for m in members: print(f"  Member user_id: {m.user_id}, workspace_id: {m.workspace_id}")

asyncio.run(check())
