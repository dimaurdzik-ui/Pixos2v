import uuid
from sqlalchemy import Column, String, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

class IntegrationConnection(Base, TimestampMixin):
    __tablename__ = "integration_connections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    provider = Column(String(100), nullable=False) # e.g., 'gmail', 'github', 'slack'
    encrypted_token = Column(String, nullable=True)
    refresh_token = Column(String, nullable=True)
    expires_at = Column(String, nullable=True)
    account_email = Column(String, nullable=True)
    scopes = Column(JSON, nullable=True)
    status = Column(String(50), nullable=False, default="not_connected") # connected, degraded, disabled, not_connected
    
    # Relationships
    workspace = relationship("Workspace")
