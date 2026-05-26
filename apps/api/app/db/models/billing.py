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

class CreditTransaction(Base, TimestampMixin):
    __tablename__ = "credit_transactions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    amount = Column(Integer, nullable=False)
    transaction_type = Column(String(50), nullable=False) # e.g. "purchase", "bonus", "refund"
    stripe_payment_id = Column(String, nullable=True)
    status = Column(String(50), nullable=False, default="completed")

class Plan(Base, TimestampMixin):
    __tablename__ = "plans"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    stripe_price_id = Column(String, nullable=True)
    credits_per_month = Column(Integer, nullable=False, default=0)
    price_usd = Column(Integer, nullable=False, default=0)

class Subscription(Base, TimestampMixin):
    __tablename__ = "subscriptions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("plans.id", ondelete="SET NULL"), nullable=True)
    stripe_subscription_id = Column(String, nullable=True)
    status = Column(String(50), nullable=False, default="active")
    current_period_end = Column(String, nullable=True)

class StripeEvent(Base, TimestampMixin):
    __tablename__ = "stripe_events"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    stripe_event_id = Column(String, unique=True, index=True, nullable=False)
    event_type = Column(String, nullable=False)
    status = Column(String(50), default="processed", nullable=False)
