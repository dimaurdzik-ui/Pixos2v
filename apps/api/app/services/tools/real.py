import asyncio
from typing import Any, Dict
from .base import BaseAdapter

class RealSearchAdapter(BaseAdapter):
    async def execute(self, payload: Dict[str, Any], context: Dict[str, Any] = None) -> Any:
        raise ValueError("Integration required: Search API not configured.")

class RealGmailAdapter(BaseAdapter):
    async def execute(self, payload: Dict[str, Any], context: Dict[str, Any] = None) -> Any:
        raise ValueError("Integration required: Google Workspace OAuth not configured.")
