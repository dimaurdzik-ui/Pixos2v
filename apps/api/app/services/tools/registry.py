from typing import Type, Dict, Any, Optional
from pydantic import BaseModel
from pydantic import BaseModel
from .base import BaseAdapter
from .mock import MockSearchAdapter, MockGmailAdapter
from .artifacts import ArtifactsAdapter

class ToolDefinition(BaseModel):
    name: str
    description: str
    default_risk_level: str
    parameters: Dict[str, Any]
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
        
    @classmethod
    def get_all_schemas(cls) -> list[Dict[str, Any]]:
        schemas = []
        for tool in cls._tools.values():
            schemas.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters
                }
            })
        return schemas

# Register core tools
ToolRegistry.register(ToolDefinition(
    name="web.search",
    description="Search the web for information based on a query.",
    default_risk_level="LOW",
    parameters={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "The search query"}
        },
        "required": ["query"]
    },
    adapter_cls=MockSearchAdapter # Would be RealSearchAdapter
))

ToolRegistry.register(ToolDefinition(
    name="gmail.send",
    description="Send an email to a recipient.",
    default_risk_level="HIGH",
    parameters={
        "type": "object",
        "properties": {
            "to": {"type": "string", "description": "Recipient email address"},
            "subject": {"type": "string", "description": "Email subject"},
            "body": {"type": "string", "description": "Email body content"},
            "action": {"type": "string", "enum": ["send"], "default": "send"}
        },
        "required": ["to", "subject", "body"]
    },
    adapter_cls=MockGmailAdapter # Would be RealGmailAdapter
))

ToolRegistry.register(ToolDefinition(
    name="gmail.search",
    description="Search emails in the inbox.",
    default_risk_level="LOW",
    parameters={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Gmail search query (e.g. is:unread)"}
        },
        "required": ["query"]
    },
    adapter_cls=MockGmailAdapter
))

ToolRegistry.register(ToolDefinition(
    name="artifacts.save",
    description="Save a markdown document, report, or code snippet as an artifact.",
    default_risk_level="LOW",
    parameters={
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Title or filename for the artifact"},
            "content": {"type": "string", "description": "The markdown content of the artifact"},
            "artifact_type": {"type": "string", "description": "Type of content, usually 'markdown' or 'code'"}
        },
        "required": ["name", "content"]
    },
    adapter_cls=ArtifactsAdapter
))
