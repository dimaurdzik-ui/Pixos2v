import asyncio
from typing import Any, Dict
from .base import BaseAdapter

class MockSearchAdapter(BaseAdapter):
    async def execute(self, payload: Dict[str, Any]) -> Any:
        query = payload.get("query", "unknown")
        await asyncio.sleep(1) # simulate latency
        return f"Searched for {query}. Found mock results."

class MockGmailAdapter(BaseAdapter):
    async def execute(self, payload: Dict[str, Any]) -> Any:
        action = payload.get("action", "send")
        await asyncio.sleep(1)
        if action == "send":
            return f"Mock email sent to {payload.get('to')}."
        return "Mock email read successfully."
