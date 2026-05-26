import enum

class TaskStatus(str, enum.Enum):
    pending = "pending"
    queued = "queued"
    running = "running"
    waiting_approval = "waiting_approval"
    waiting_connection = "waiting_connection"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"

class WorkflowRunStatus(str, enum.Enum):
    queued = "queued"
    running = "running"
    paused_for_approval = "paused_for_approval"
    waiting_connection = "waiting_connection"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"

class ApprovalStatus(str, enum.Enum):
    pending = "pending"
    executing = "executing"
    executed = "executed"
    rejected = "rejected"
    failed = "failed"
    expired = "expired"

class WorkflowSource(str, enum.Enum):
    task = "task"
    chat = "chat"
    schedule = "schedule"
    api = "api"
