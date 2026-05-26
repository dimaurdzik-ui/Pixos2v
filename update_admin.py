import asyncio
from apps.api.app.db.database import AsyncSessionLocal
from apps.api.app.db.models.core import User
from sqlalchemy import select

async def main():
    async with AsyncSessionLocal() as db:
        users = await db.execute(select(User))
        for u in users.scalars().all():
            if "clerk.user" in u.email:
                u.is_super_admin = True
                print(f"Updated {u.email} to super admin.")
        await db.commit()

asyncio.run(main())
