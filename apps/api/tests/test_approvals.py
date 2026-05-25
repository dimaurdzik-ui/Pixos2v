import pytest
import uuid
from httpx import AsyncClient, ASGITransport
from apps.api.app.main import app

@pytest.mark.asyncio
async def test_approval_endpoints_not_found():
    # Test that approving a non-existent approval ID returns 404
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res1 = await ac.post(f"/api/v1/approvals/{uuid.uuid4()}/approve")
        res2 = await ac.post(f"/api/v1/approvals/{uuid.uuid4()}/reject")
        
    assert res1.status_code == 404
    assert res2.status_code == 404
