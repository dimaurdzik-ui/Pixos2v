import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from apps.api.app.core.config import settings

# Use NullPool in tests so connections are never shared across event loops
if os.getenv("TESTING") == "1":
    from sqlalchemy.pool import NullPool
    engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI, echo=False, poolclass=NullPool)
else:
    engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
