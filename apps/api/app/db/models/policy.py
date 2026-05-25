import uuid
from sqlalchemy import Column, String, ForeignKey, JSON, DateTime, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID
from .base import Base, TimestampMixin

class ToolPolicy(Base, TimestampMixin):
    __tablename__ = "tool_policies"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    tool_name = Column(String, nullable=False)
    risk_level = Column(String, nullable=False) # e.g. READ, DRAFT, EXTERNAL_WRITE
    approval_required = Column(String, nullable=False) # auto, approval_optional, approval_required
    autonomy_level = Column(String, nullable=True)
    allowed_roles = Column(JSON, nullable=True) # array of roles
    allowed_destinations = Column(JSON, nullable=True) # allowlist domains/emails
    max_daily_actions = Column(Integer, nullable=True)
    is_enabled = Column(Boolean, nullable=False, default=True)

class PendingApproval(Base, TimestampMixin):
    __tablename__ = "pending_approvals"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    workflow_run_id = Column(UUID(as_uuid=True), ForeignKey("workflow_runs.id", ondelete="CASCADE"), nullable=False)
    tool_call_id = Column(String, nullable=False)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    requested_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    risk_level = Column(String, nullable=False)
    action_type = Column(String, nullable=False)
    summary = Column(String, nullable=True)
    payload_preview = Column(JSON, nullable=True)
    full_payload_encrypted = Column(String, nullable=True)
    status = Column(String, nullable=False, default="pending") # pending, approved, rejected
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    rejected_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    rejected_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    idempotency_key = Column(String, nullable=True, unique=True)
