import uuid
from sqlalchemy import Column, String, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

class Conversation(Base, TimestampMixin):
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=True)
    
    # Relationships
    workspace = relationship("Workspace")
    agent = relationship("Agent")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan", order_by="Message.created_at")

class Message(Base, TimestampMixin):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    sender_type = Column(String(50), nullable=False) # 'user', 'agent', 'system', 'tool'
    content = Column(String, nullable=True)
    tool_calls = Column(JSON, nullable=True) # list of tool_call dicts
    artifact_id = Column(UUID(as_uuid=True), ForeignKey("artifacts.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    artifact = relationship("Artifact")
