import uuid
from sqlalchemy import Column, ForeignKey, Integer, String, JSON
from sqlalchemy.dialects.postgresql import UUID
from .base import Base, TimestampMixin

class CreditBalance(Base, TimestampMixin):
    __tablename__ = "credit_balances"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, unique=True)
    balance = Column(Integer, default=0, nullable=False)

class UsageRecord(Base, TimestampMixin):
    __tablename__ = "usage_records"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    workflow_run_id = Column(UUID(as_uuid=True), ForeignKey("workflow_runs.id", ondelete="SET NULL"), nullable=True)
    cost = Column(Integer, nullable=False)
    description = Column(String, nullable=True)
    metadata_ = Column("metadata", JSON, nullable=True)
