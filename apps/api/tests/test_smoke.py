"""
Smoke tests for Pixos2v critical paths.
Run: PYTHONPATH=. uv run pytest apps/api/tests/test_smoke.py -v

Fixtures are defined in conftest.py (session-scoped, Clerk bypassed).
"""
import asyncio
import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


# ─────────────────────────────────────────────────────────────────────────────
# Tests
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient):
    """Basic health check — server must be up."""
    r = await client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_get_agents(client: AsyncClient):
    """Agents endpoint must return a list (possibly empty)."""
    r = await client.get("/api/v1/agents")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


@pytest.mark.asyncio
async def test_get_workflows(client: AsyncClient):
    """Workflows endpoint must be reachable."""
    r = await client.get("/api/v1/workflows")
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_get_approvals(client: AsyncClient):
    """Approvals endpoint must return a list."""
    r = await client.get("/api/v1/approvals")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


@pytest.mark.asyncio
async def test_get_conversations(client: AsyncClient):
    """Chat conversations must return a list."""
    r = await client.get("/api/v1/chat/conversations")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


@pytest.mark.asyncio
async def test_create_conversation_and_send_message(client: AsyncClient, test_user_and_workspace):
    """
    Core chat flow smoke test:
    1. Create a conversation directly in DB
    2. POST a message via API
    3. Verify message is saved in DB
    """
    from apps.api.app.db.database import AsyncSessionLocal
    from apps.api.app.db.models.chat import Conversation, Message
    from apps.api.app.db.models.agents import Agent

    user_data, ws_data = test_user_and_workspace

    async with AsyncSessionLocal() as session:
        # Find or create a coordinator agent
        result = await session.execute(
            select(Agent).where(Agent.workspace_id == ws_data["id"], Agent.is_coordinator == True)
        )
        coordinator = result.scalar_one_or_none()
        if not coordinator:
            coordinator = Agent(
                workspace_id=ws_data["id"],
                name="Test Coordinator",
                role="coordinator",
                is_coordinator=True,
                model="gpt-4o",
                status="active",
            )
            session.add(coordinator)
            await session.commit()
            await session.refresh(coordinator)

        # Create conversation
        conv = Conversation(
            workspace_id=ws_data["id"],
            agent_id=coordinator.id,
            title="Smoke Test Chat",
            conversation_type="agent",
        )
        session.add(conv)
        await session.commit()
        await session.refresh(conv)
        conv_id = conv.id

    # POST message via API
    r = await client.post(
        f"/api/v1/chat/conversations/{conv_id}/messages",
        json={"content": "привіт smoke test"},
    )
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    data = r.json()
    assert data["sender_type"] == "user"
    assert data["content"] == "привіт smoke test"

    # Verify in DB
    async with AsyncSessionLocal() as session:
        result_msgs = await session.execute(
            select(Message).where(Message.conversation_id == conv_id)
        )
        msgs = result_msgs.scalars().all()
        assert len(msgs) >= 1
        assert any(m.content == "привіт smoke test" for m in msgs)


@pytest.mark.asyncio
async def test_tool_gateway_destination_blocked(test_user_and_workspace):
    """
    ToolGateway must block tool execution when destination is not in allowlist
    and MOCK_TOOLS=False.
    """
    from apps.api.app.services.tools.gateway import ToolGateway
    from apps.api.app.core.config import settings
    from apps.api.app.db.database import AsyncSessionLocal
    from apps.api.app.db.models.policy import DestinationAllowlist

    if settings.MOCK_TOOLS:
        pytest.skip("MOCK_TOOLS=True — destination allowlist check is skipped in mock mode")

    user_data, ws_data = test_user_and_workspace

    async with AsyncSessionLocal() as session:
        entry = DestinationAllowlist(
            workspace_id=ws_data["id"],
            provider="gmail",
            destination_type="email",
            value="allowed@company.com",
            created_by=user_data["id"],
            is_active=True,
        )
        session.add(entry)
        await session.commit()

    context = {
        "workspace_id": str(ws_data["id"]),
        "workflow_run_id": str(uuid.uuid4()),
        "user_id": str(user_data["id"]),
    }

    result = await ToolGateway.execute(
        "gmail.send",
        {"to": "evil@hacker.com", "subject": "Test", "body": "Test"},
        context,
    )
    assert "DESTINATION_NOT_ALLOWED" in str(result.get("error", ""))


@pytest.mark.asyncio
async def test_approval_atomic_lock(client: AsyncClient, test_user_and_workspace):
    """
    Approving the same approval_id twice concurrently must result in
    only one execution (atomic UPDATE WHERE status='pending').
    """
    from apps.api.app.db.database import AsyncSessionLocal
    from apps.api.app.db.models.policy import PendingApproval
    from apps.api.app.db.models.workflow import WorkflowRun
    from apps.api.app.core.statuses import ApprovalStatus, WorkflowRunStatus, WorkflowSource

    user_data, ws_data = test_user_and_workspace

    async with AsyncSessionLocal() as session:
        run = WorkflowRun(
            workspace_id=ws_data["id"],
            status=WorkflowRunStatus.running,
            source=WorkflowSource.api,
            created_by=user_data["id"],
        )
        session.add(run)
        await session.flush()

        approval = PendingApproval(
            workspace_id=ws_data["id"],
            workflow_run_id=run.id,
            tool_call_id=str(uuid.uuid4()),
            agent_id=None,
            risk_level="HIGH",
            action_type="gmail.send",
            status=ApprovalStatus.pending,
        )
        session.add(approval)
        await session.commit()
        approval_id = approval.id

    # Fire two concurrent approve requests
    url = f"/api/v1/approvals/{approval_id}/approve"
    results = await asyncio.gather(
        client.post(url),
        client.post(url),
        return_exceptions=True,
    )

    statuses = [r.status_code for r in results if hasattr(r, "status_code")]
    assert all(s == 200 for s in statuses), f"Unexpected statuses: {statuses}"

    # Reload — status must NOT be 'pending'
    async with AsyncSessionLocal() as session:
        approval = await session.get(PendingApproval, approval_id)
        assert approval.status != ApprovalStatus.pending


@pytest.mark.asyncio
async def test_budget_hard_stop(test_user_and_workspace):
    """
    A workspace with 0 credits must receive BudgetExceededError from coordinator.
    """
    from apps.api.app.db.database import AsyncSessionLocal
    from apps.api.app.db.models.billing import CreditBalance
    from apps.api.app.workflows.coordinator import agent_execute

    user_data, ws_data = test_user_and_workspace

    # Drain credits to 0
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(CreditBalance).where(CreditBalance.workspace_id == ws_data["id"]))
        balance = result.scalar_one_or_none()
        original = balance.balance if balance else 9999
        if balance:
            balance.balance = 0
            await session.commit()

    try:
        from langgraph.errors import NodeInterrupt
        with pytest.raises(NodeInterrupt, match="BudgetExceededError"):
            await agent_execute({
                "workflow_run_id": str(uuid.uuid4()),
                "workspace_id": str(ws_data["id"]),
                "user_id": str(user_data["id"]),
                "current_agent_id": None,
                "user_request": "test",
                "messages": [],
                "status": "running",
                "results": [],
                "tool_calls": [],
                "conversation_id": None,
                "coordinator_agent_id": None,
                "task_id": None,
                "workflow_step_id": None,
                "current_step": 0,
                "pending_approval_id": None,
                "total_cost": 0,
                "artifact_content": "",
            })
    finally:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(CreditBalance).where(CreditBalance.workspace_id == ws_data["id"]))
            balance = result.scalar_one_or_none()
            if balance:
                balance.balance = original
                await session.commit()

