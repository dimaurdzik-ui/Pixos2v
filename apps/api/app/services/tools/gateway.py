from typing import Any, Dict
from apps.api.app.core.config import settings
from .registry import ToolRegistry
from apps.api.app.db.database import AsyncSessionLocal
from apps.api.app.db.models.integrations import IntegrationConnection
from apps.api.app.core.security import decrypt_token
from sqlalchemy import select
import uuid

class ToolGateway:
    @staticmethod
    async def execute(tool_name: str, payload: Dict[str, Any], context: Dict[str, Any] = None) -> Any:
        # If the tool is provider-specific (e.g., gmail.send, github.create_issue)
        provider = tool_name.split('.')[0] if '.' in tool_name else None
        
        # Check connection if it's a real tool and context has workspace_id
        if not settings.MOCK_TOOLS and provider and context and "workspace_id" in context:
            # We don't require connection for generic tools like 'web' or 'artifacts'
            if provider not in ["web", "artifacts"]:
                async with AsyncSessionLocal() as db:
                    result = await db.execute(
                        select(IntegrationConnection)
                        .where(
                            IntegrationConnection.workspace_id == uuid.UUID(context["workspace_id"]),
                            IntegrationConnection.provider == provider,
                            IntegrationConnection.status == "connected"
                        )
                    )
                    connection = result.scalar_one_or_none()
                    if not connection:
                        raise ValueError("CONNECTION_REQUIRED")
                        
                    # Decrypt the token and inject it into the context for the adapter
                    if connection.encrypted_token:
                        plain_token = decrypt_token(connection.encrypted_token)
                        context["access_token"] = plain_token

        adapter = ToolRegistry.get_adapter(tool_name, use_mock=settings.MOCK_TOOLS)
        if not adapter:
            raise ValueError(f"Tool {tool_name} not found in registry.")
            
        # Execute the adapter
        result = await adapter.execute(payload, context)
        return result
