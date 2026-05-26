import uuid
from sqlalchemy import Column, String, ForeignKey, JSON, DateTime, Integer, Boolean, Enum
from sqlalchemy.dialects.postgresql import UUID
from .base import Base, TimestampMixin
from apps.api.app.core.statuses import ApprovalStatus

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
    tool_execution_id = Column(UUID(as_uuid=True), ForeignKey("tool_executions.id", ondelete="CASCADE"), nullable=True)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), nullable=True)
    requested_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    risk_level = Column(String, nullable=False)
    action_type = Column(String, nullable=False)
    summary = Column(String, nullable=True)
    payload_preview = Column(JSON, nullable=True)
    full_payload_encrypted = Column(String, nullable=True)
    approval_payload_hash = Column(String, nullable=True)
    status = Column(Enum(ApprovalStatus), nullable=False, default=ApprovalStatus.pending)
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    rejected_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    rejected_at = Column(DateTime(timezone=True), nullable=True)
    executed_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    idempotency_key = Column(String, nullable=True, unique=True)

class ToolExecution(Base, TimestampMixin):
    __tablename__ = "tool_executions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    workflow_run_id = Column(UUID(as_uuid=True), ForeignKey("workflow_runs.id", ondelete="CASCADE"), nullable=False)
    workflow_step_id = Column(UUID(as_uuid=True), ForeignKey("workflow_steps.id", ondelete="SET NULL"), nullable=True)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="SET NULL"), nullable=True)
    tool_name = Column(String, nullable=False)
    risk_level = Column(String, nullable=False)
    status = Column(String, nullable=False, default="pending")
    request_payload_encrypted = Column(String, nullable=True)
    payload_preview = Column(JSON, nullable=True)
    result_payload = Column(JSON, nullable=True)
    error_message = Column(String, nullable=True)
    idempotency_key = Column(String, nullable=True, unique=True)
    external_idempotency_key = Column(String, nullable=True)
    approval_id = Column(UUID(as_uuid=True), ForeignKey("pending_approvals.id", ondelete="SET NULL"), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

class PolicyDecision(Base, TimestampMixin):
    __tablename__ = "policy_decisions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    workflow_run_id = Column(UUID(as_uuid=True), ForeignKey("workflow_runs.id", ondelete="CASCADE"), nullable=False)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="SET NULL"), nullable=True)
    tool_name = Column(String, nullable=False)
    decision = Column(String, nullable=False) # allow, require_approval, deny, connection_required
    reason = Column(String, nullable=True)
    policy_snapshot = Column(JSON, nullable=True)

class DestinationAllowlist(Base, TimestampMixin):
    __tablename__ = "destination_allowlists"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    provider = Column(String, nullable=False)
    destination_type = Column(String, nullable=False)
    value = Column(String, nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
