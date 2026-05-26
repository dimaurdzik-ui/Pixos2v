import uuid
from sqlalchemy import Column, String, ForeignKey, JSON, DateTime
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

class IntegrationToken(Base, TimestampMixin):
    __tablename__ = "integration_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    connection_id = Column(UUID(as_uuid=True), ForeignKey("integration_connections.id", ondelete="CASCADE"), nullable=False)
    provider = Column(String(100), nullable=False)
    encrypted_access_token = Column(String, nullable=False)
    encrypted_refresh_token = Column(String, nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    connection = relationship("IntegrationConnection")

class OAuthState(Base, TimestampMixin):
    __tablename__ = "oauth_states"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    state_token = Column(String(255), unique=True, nullable=False)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    provider = Column(String(100), nullable=False)
    redirect_uri = Column(String, nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
