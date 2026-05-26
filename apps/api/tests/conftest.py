"""
conftest.py — pytest fixtures for Pixos2v test suite.

Design:
- Patches the SQLAlchemy engine to use NullPool (no connection reuse across loops)
- Session-scoped db setup for user/workspace creation  
- Function-scoped client per test with dependency_overrides (Clerk bypassed)
"""
import asyncio
import os
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select

# ─── Must be set BEFORE any app modules are imported ────────────────────────
os.environ.setdefault("TESTING", "1")
# ─────────────────────────────────────────────────────────────────────────────
# Create/reuse test user + workspace (runs once, commits, then uses a fresh session)
# ─────────────────────────────────────────────────────────────────────────────

@pytest_asyncio.fixture(scope="session")
async def test_user_and_workspace():
    from apps.api.app.db.database import AsyncSessionLocal
    from apps.api.app.db.models.core import User, Workspace, WorkspaceMember
    from apps.api.app.db.models.billing import CreditBalance

    email = "smoke_test@pixos.test"

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user:
            user = User(email=email, full_name="Smoke Test User", is_super_admin=False)
            session.add(user)
            await session.flush()

            ws = Workspace(name="Smoke Test Workspace", created_by=user.id)
            session.add(ws)
            await session.flush()

            session.add(WorkspaceMember(workspace_id=ws.id, user_id=user.id, role="owner"))
            session.add(CreditBalance(workspace_id=ws.id, balance=9999))

            await session.commit()
            await session.refresh(user)
            await session.refresh(ws)
        else:
            result_ws = await session.execute(
                select(Workspace)
                .join(WorkspaceMember, WorkspaceMember.workspace_id == Workspace.id)
                .where(WorkspaceMember.user_id == user.id)
                .limit(1)
            )
            ws = result_ws.scalar_one()

    # Return plain dicts/ids to avoid session-boundary issues
    return {"id": user.id, "email": user.email, "full_name": user.full_name, "is_super_admin": user.is_super_admin}, \
           {"id": ws.id, "name": ws.name}


# ─────────────────────────────────────────────────────────────────────────────
# Per-test HTTP client with dependency_overrides (function-scoped)
# ─────────────────────────────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def client(test_user_and_workspace):
    from apps.api.app.main import app
    from apps.api.app.api import deps
    from apps.api.app.db.models.core import User, Workspace
    from sqlalchemy.orm import make_transient

    user_data, ws_data = test_user_and_workspace

    # Re-fetch fresh detached objects for each test
    from apps.api.app.db.database import AsyncSessionLocal
    async with AsyncSessionLocal() as session:
        user = await session.get(User, user_data["id"])
        ws = await session.get(Workspace, ws_data["id"])
        # Detach from session so they don't conflict with request sessions
        session.expunge(user)
        session.expunge(ws)

    async def _fake_user():
        return user

    async def _fake_workspace():
        return ws

    app.dependency_overrides[deps.get_current_user] = _fake_user
    app.dependency_overrides[deps.get_current_workspace] = _fake_workspace

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c

    app.dependency_overrides.pop(deps.get_current_user, None)
    app.dependency_overrides.pop(deps.get_current_workspace, None)

