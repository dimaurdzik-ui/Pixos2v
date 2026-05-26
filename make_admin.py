import asyncio
from apps.api.app.db.database import AsyncSessionLocal
from apps.api.app.db.models.core import User
from sqlalchemy import select

async def main():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.clerk_id == 'user_3EEdw9kWsRaPDxJ1aMEX8tca2FT'))
        u = result.scalar_one_or_none()
        if u:
            u.is_super_admin = True
            u.email = "dima.urdzik@gmail.com"
            await session.commit()
            print(f"Made user {u.id} a super admin and updated email!")
        else:
            print("User not found")

asyncio.run(main())
