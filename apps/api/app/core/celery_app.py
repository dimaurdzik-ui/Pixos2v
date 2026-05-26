import os
from celery import Celery

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "pixos_worker",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["apps.api.app.tasks.worker"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    # Enterprise settings
    task_acks_late=True, # Idempotency: acknowledge task only after successful execution
    task_reject_on_worker_lost=True, # Re-queue task if worker crashes
    worker_prefetch_multiplier=1, # Fair dispatch
    task_time_limit=3600, # 1 hour hard timeout
    task_soft_time_limit=3300, # 55 min soft timeout
    task_default_queue="celery_default",
)

# Route workflows to a dedicated queue
celery_app.conf.task_routes = {
    "tasks.worker.run_coordinator_task": {"queue": "celery_workflows"},
}
