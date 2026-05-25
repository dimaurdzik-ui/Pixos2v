from typing import Any, Dict
from apps.api.app.core.config import settings
from .registry import ToolRegistry

class ToolGateway:
    @staticmethod
    async def execute(tool_name: str, payload: Dict[str, Any]) -> Any:
        adapter = ToolRegistry.get_adapter(tool_name, use_mock=settings.MOCK_TOOLS)
        if not adapter:
            raise ValueError(f"Tool {tool_name} not found in registry.")
            
        # Execute the adapter
        result = await adapter.execute(payload)
        return result
