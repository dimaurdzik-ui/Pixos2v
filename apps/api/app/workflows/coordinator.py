from typing import TypedDict, Annotated, Sequence, Optional
from langgraph.graph import StateGraph, START, END
import uuid
import json

from apps.api.app.services.llm import LLMService
from apps.api.app.db.database import AsyncSessionLocal
from apps.api.app.db.models.workflow import WorkflowRun, WorkflowStep, Task
from apps.api.app.db.models.outputs import Artifact
from apps.api.app.db.models.billing import UsageRecord
from apps.api.app.db.models.policy import PendingApproval
from apps.api.app.db.models.core import AuditLog

from apps.api.app.policies.registry import get_tool_risk, AutonomyLevel
from apps.api.app.policies.checker import requires_approval

class CoordinatorState(TypedDict):
    workflow_run_id: str
    task_id: str
    workspace_id: str
    user_request: str
    current_step: int
    results: list[str]
    total_cost: float
    artifact_content: str
    tool_calls: list[dict] # e.g. [{"tool": "gmail.send", "payload": {"to": "test@test"}}]
    pending_approval_id: Optional[str]
    status: str # "running", "paused_for_approval", "completed"

async def start_run(state: CoordinatorState):
    """Initializes the workflow step in DB"""
    async with AsyncSessionLocal() as db:
        run = await db.get(WorkflowRun, uuid.UUID(state["workflow_run_id"]))
        if run:
            run.status = "running"
            await db.commit()
    return {"current_step": 1, "results": [], "total_cost": 0.0, "status": "running"}

async def coordinator_plan(state: CoordinatorState):
    """Coordinator decides the plan using LLM"""
    if state.get("pending_approval_id"):
        # We resumed from an approval, skip planning
        return {}

    messages = [
        {"role": "system", "content": "You are a coordinator AI. Create a simple execution plan for the user's task."},
        {"role": "user", "content": state["user_request"]}
    ]
    response = await LLMService.generate_completion(messages)
    
    return {
        "results": state["results"] + [f"Coordinator planned: {response['content']}"],
        "total_cost": state["total_cost"] + response["cost_in_usd"]
    }

async def agent_execute(state: CoordinatorState):
    """Agent figures out which tool to run"""
    if state.get("pending_approval_id"):
        # We resumed from an approval, skip this and go straight to execution
        return {}

    tool_calls = []
    req = state["user_request"].lower()
    if "email" in req or "send" in req:
        tool_calls.append({"tool": "gmail.send", "payload": {"to": "user@example.com", "body": "Hello"}})
    elif "search" in req or "find" in req or "news" in req:
        tool_calls.append({"tool": "web.search", "payload": {"query": state["user_request"]}})
    else:
        # Default read action
        tool_calls.append({"tool": "gmail.search", "payload": {"query": "test"}})

    return {"tool_calls": tool_calls}

async def check_policy(state: CoordinatorState):
    """Checks tools against policies. Interrupts if approval needed."""
    if state.get("pending_approval_id"):
        # We resumed, clear it so we can execute
        return {"pending_approval_id": None}

    # Simplification: we check the first tool
    if not state.get("tool_calls"):
        return {}

    tool_call = state["tool_calls"][0]
    tool_name = tool_call["tool"]
    risk = get_tool_risk(tool_name)
    
    # Assume agents have BALANCED autonomy for now
    needs_approval = requires_approval(AutonomyLevel.BALANCED, risk)

    if needs_approval:
        async with AsyncSessionLocal() as db:
            approval = PendingApproval(
                workspace_id=uuid.UUID(state["workspace_id"]),
                workflow_run_id=uuid.UUID(state["workflow_run_id"]),
                tool_call_id=str(uuid.uuid4()), # idempotency_key equivalent
                agent_id=uuid.uuid4(), # Mock agent ID
                risk_level=risk,
                action_type=tool_name,
                payload_preview=tool_call["payload"],
                status="pending"
            )
            db.add(approval)
            await db.commit()
            await db.refresh(approval)
            
            # Update run status
            run = await db.get(WorkflowRun, uuid.UUID(state["workflow_run_id"]))
            run.status = "paused_for_approval"
            await db.commit()
            
            return {"pending_approval_id": str(approval.id), "status": "paused_for_approval", "results": state["results"] + [f"Paused for approval: {tool_name}"]}
            
    return {"status": "running"}

async def execute_tools(state: CoordinatorState):
    """Executes the approved or safe tools."""
    if state["status"] == "paused_for_approval":
        # Do not execute, we are paused
        return {}

    import asyncio

    tool_results = []
    for tc in state.get("tool_calls", []):
        if tc["tool"] == "web.search":
            # Simulate real web search delay and response
            await asyncio.sleep(2)
            result = f"Found 3 articles about '{tc['payload'].get('query', '')}':\\n1. AI is changing the world.\\n2. Next.js 15 Released.\\n3. Python 3.14 features."
            tool_results.append(result)
        else:
            # Mock execution for others
            tool_results.append(f"Executed {tc['tool']} successfully.")
        
        # Log Audit
        async with AsyncSessionLocal() as db:
            log = AuditLog(
                workspace_id=uuid.UUID(state["workspace_id"]),
                actor_type="system",
                action="tool_executed",
                resource_type="tool",
                resource_id=tc["tool"],
                metadata_=tc["payload"]
            )
            db.add(log)
            await db.commit()

    return {
        "artifact_content": "\\n".join(tool_results),
        "results": state["results"] + tool_results
    }

async def save_artifact(state: CoordinatorState):
    if state["status"] == "paused_for_approval":
        return {}

    async with AsyncSessionLocal() as db:
        artifact = Artifact(
            workspace_id=uuid.UUID(state["workspace_id"]),
            workflow_run_id=uuid.UUID(state["workflow_run_id"]),
            name=f"Result for Task {state['task_id'][:8]}",
            content=state.get("artifact_content", "No output"),
            artifact_type="task_result"
        )
        db.add(artifact)
        await db.commit()
    return {"results": state["results"] + ["Artifact saved."]}

async def end_run(state: CoordinatorState):
    if state["status"] == "paused_for_approval":
        return {}

    async with AsyncSessionLocal() as db:
        run = await db.get(WorkflowRun, uuid.UUID(state["workflow_run_id"]))
        if run:
            run.status = "completed"
            run.total_cost = int(state["total_cost"] * 100)
            
        task = await db.get(Task, uuid.UUID(state["task_id"]))
        if task:
            task.status = "completed"

        usage = UsageRecord(
            workspace_id=uuid.UUID(state["workspace_id"]),
            workflow_run_id=uuid.UUID(state["workflow_run_id"]),
            cost=int(state["total_cost"] * 100),
            description="Workflow Execution LLM Cost"
        )
        db.add(usage)
        await db.commit()
    return {"results": state["results"] + ["Run finished."], "status": "completed"}

# Define routing function
def route_after_policy(state: CoordinatorState):
    if state["status"] == "paused_for_approval":
        return END # Pause execution and return to user
    return "execute_tools"

# Define the LangGraph workflow
workflow = StateGraph(CoordinatorState)

workflow.add_node("start_run", start_run)
workflow.add_node("coordinator_plan", coordinator_plan)
workflow.add_node("agent_execute", agent_execute)
workflow.add_node("check_policy", check_policy)
workflow.add_node("execute_tools", execute_tools)
workflow.add_node("save_artifact", save_artifact)
workflow.add_node("end_run", end_run)

workflow.add_edge(START, "start_run")
workflow.add_edge("start_run", "coordinator_plan")
workflow.add_edge("coordinator_plan", "agent_execute")
workflow.add_edge("agent_execute", "check_policy")

# Conditional routing based on policy
workflow.add_conditional_edges("check_policy", route_after_policy)

workflow.add_edge("execute_tools", "save_artifact")
workflow.add_edge("save_artifact", "end_run")
workflow.add_edge("end_run", END)

# Compile graph
coordinator_app = workflow.compile()
