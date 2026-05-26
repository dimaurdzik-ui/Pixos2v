import asyncio
import logging
from apps.api.app.core.celery_app import celery_app
import uuid

logger = logging.getLogger(__name__)

def run_async(coro):
    """Helper to run async code inside a synchronous Celery task"""
    return asyncio.get_event_loop().run_until_complete(coro)

@celery_app.task(name="tasks.worker.run_coordinator_task")
def run_coordinator_task(initial_state: dict):
    """
    Executes the Coordinator graph as a background Celery task.
    """
    async def _async_run():
        try:
            # We import here to avoid circular dependencies and ensure DB setup inside the worker
            from apps.api.app.workflows.coordinator import coordinator_app
            from apps.api.app.db.database import AsyncSessionLocal
            from apps.api.app.db.models.billing import CreditBalance, UsageRecord
            from apps.api.app.db.models.workflow import WorkflowRun
            from sqlalchemy import select
            
            run_id = initial_state.get("workflow_run_id")
            
            # Use checkpointer thread_id to persist and group the state
            config = {"configurable": {"thread_id": run_id}}
            
            # Invoke the LangGraph coordinator
            # If graph is waking up (resume), initial_state will typically be None 
            # and we just rely on thread_id, or we pass state updates directly.
            final_state = await coordinator_app.ainvoke(initial_state, config=config)
            
            # If the graph has fully completed (not just paused)
            if final_state and final_state.get("status") == "completed":
                async with AsyncSessionLocal() as db:
                    run = await db.get(WorkflowRun, uuid.UUID(run_id))
                    if run:
                        run.status = "completed"
                        
                        # Get real cost calculated by LLM
                        calculated_cost = int(final_state.get("total_cost", 10))
                        # Prevent 0 cost if it actually ran but returned small float
                        if calculated_cost == 0 and final_state.get("total_cost", 0) > 0:
                            calculated_cost = 1
                            
                        result = await db.execute(select(CreditBalance).where(CreditBalance.workspace_id == run.workspace_id))
                        balance = result.scalars().first()
                        if balance:
                            balance.balance -= calculated_cost
                            usage = UsageRecord(
                                workspace_id=run.workspace_id,
                                workflow_run_id=run.id,
                                cost=calculated_cost
                            )
                            db.add(usage)
                        
                    await db.commit()
                    
            return final_state
        except Exception as e:
            logger.error(f"Coordinator failed: {e}")
            from apps.api.app.db.database import AsyncSessionLocal
            from apps.api.app.db.models.workflow import WorkflowRun
            async with AsyncSessionLocal() as db:
                run = await db.get(WorkflowRun, uuid.UUID(initial_state["workflow_run_id"]))
                if run:
                    run.status = "failed"
                    await db.commit()
            raise e

    # Since Celery uses a multi-processing pool, we can create a new loop safely
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_async_run())
    finally:
        loop.close()
