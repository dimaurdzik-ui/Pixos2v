from typing import Type, Dict, Optional
from pydantic import BaseModel
from .base import BaseAdapter
from .mock import MockSearchAdapter, MockGmailAdapter

class ToolDefinition(BaseModel):
    name: str
    description: str
    default_risk_level: str
    adapter_cls: Type[BaseAdapter]

class ToolRegistry:
    _tools: Dict[str, ToolDefinition] = {}

    @classmethod
    def register(cls, tool: ToolDefinition):
        cls._tools[tool.name] = tool
        
    @classmethod
    def get_adapter(cls, tool_name: str, use_mock: bool = False) -> Optional[BaseAdapter]:
        if tool_name not in cls._tools:
            return None
            
        if use_mock:
            # Simple mock routing for MVP
            if "search" in tool_name:
                return MockSearchAdapter()
            elif "gmail" in tool_name:
                return MockGmailAdapter()
                
        # In a real scenario, instantiate the actual adapter with credentials
        adapter_cls = cls._tools[tool_name].adapter_cls
        return adapter_cls()

# Register core tools
ToolRegistry.register(ToolDefinition(
    name="web.search",
    description="Search the web",
    default_risk_level="LOW",
    adapter_cls=MockSearchAdapter # Would be RealSearchAdapter
))

ToolRegistry.register(ToolDefinition(
    name="gmail.send",
    description="Send an email",
    default_risk_level="HIGH",
    adapter_cls=MockGmailAdapter # Would be RealGmailAdapter
))

ToolRegistry.register(ToolDefinition(
    name="gmail.search",
    description="Search emails",
    default_risk_level="LOW",
    adapter_cls=MockGmailAdapter
))
