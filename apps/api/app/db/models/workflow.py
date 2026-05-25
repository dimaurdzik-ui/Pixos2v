import uuid
from sqlalchemy import Column, String, ForeignKey, JSON, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from .base import Base, TimestampMixin

class Task(Base, TimestampMixin):
    __tablename__ = "tasks"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    description = Column(String, nullable=False)
    status = Column(String, nullable=False, default="pending") # pending, running, completed, failed

class WorkflowRun(Base, TimestampMixin):
    __tablename__ = "workflow_runs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    status = Column(String, nullable=False, default="started")
    total_cost = Column(Integer, default=0) # in cents or smallest credit unit
    
class WorkflowStep(Base, TimestampMixin):
    __tablename__ = "workflow_steps"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_run_id = Column(UUID(as_uuid=True), ForeignKey("workflow_runs.id", ondelete="CASCADE"), nullable=False)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="SET NULL"), nullable=True)
    step_order = Column(Integer, nullable=False, default=0)
    action = Column(String, nullable=False)
    status = Column(String, nullable=False, default="running")
    input_context = Column(JSON, nullable=True)
    output_summary = Column(JSON, nullable=True)
    error = Column(String, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

class WorkflowEvent(Base, TimestampMixin):
    __tablename__ = "workflow_events"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_run_id = Column(UUID(as_uuid=True), ForeignKey("workflow_runs.id", ondelete="CASCADE"), nullable=False)
    workflow_step_id = Column(UUID(as_uuid=True), ForeignKey("workflow_steps.id", ondelete="CASCADE"), nullable=True)
    sequence_number = Column(Integer, autoincrement=True)
    event_type = Column(String, nullable=False)
    visibility = Column(String, nullable=False, default="internal") # internal, customer
    payload = Column(JSON, nullable=True)
