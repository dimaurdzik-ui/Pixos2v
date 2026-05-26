import asyncio
from apps.api.app.db.database import AsyncSessionLocal
from apps.api.app.db.models.core import User
from sqlalchemy import select

async def main():
    async with AsyncSessionLocal() as db:
        # Check if user already exists
        result = await db.execute(select(User).where(User.email == "324r2rar@pixelagents.com"))
        user = result.scalar_one_or_none()
        
        if user:
            user.is_super_admin = True
            user.clerk_id = "324e2fsr2234"
            await db.commit()
            print("Updated existing user to admin")
        else:
            new_user = User(
                clerk_id="324e2fsr2234",
                email="324r2rar@pixelagents.com",
                full_name="Admin User",
                is_super_admin=True
            )
            db.add(new_user)
            await db.commit()
            print("Created new admin user")

asyncio.run(main())
