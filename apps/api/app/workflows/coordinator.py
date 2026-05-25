import uuid
import asyncio
from typing import TypedDict, Any, Optional
from langgraph.graph import StateGraph, END
from apps.api.app.db.database import AsyncSessionLocal
from apps.api.app.db.models.workflow import WorkflowStep, WorkflowEvent
from apps.api.app.db.models.policy import PendingApproval
from apps.api.app.services.tools.gateway import ToolGateway

class CoordinatorState(TypedDict):
    workflow_run_id: str
    task_id: str
    workspace_id: str
    user_id: str
    coordinator_agent_id: str
    current_agent_id: str
    workflow_step_id: Optional[str]
    user_request: str
    current_step: int
    tool_calls: list[dict] # e.g. [{"tool": "gmail.send", "payload": {...}}]
    results: list[Any]
    status: str # "running", "paused_for_approval", "completed", "failed"
    pending_approval_id: Optional[str] # if paused
    total_cost: float
    artifact_content: str

async def start_run(state: CoordinatorState):
    """Initializes the workflow step in DB"""
    async with AsyncSessionLocal() as db:
        step = WorkflowStep(
            workflow_run_id=uuid.UUID(state["workflow_run_id"]),
            step_order=state["current_step"],
            action="init",
            agent_id=uuid.UUID(state["current_agent_id"]) if state.get("current_agent_id") else None,
            status="running"
        )
        db.add(step)
        await db.commit()
        await db.refresh(step)
    return {"status": "running", "workflow_step_id": str(step.id)}

async def agent_execute(state: CoordinatorState):
    """Mock agent decision making using if/else for MVP"""
    req = state["user_request"].lower()
    
    # Mocking LiteLLM / Agent decision
    tool_calls = []
    if "email" in req:
        tool_calls.append({"tool": "gmail.send", "payload": {"to": "test@test.com", "body": "Hello"}})
    elif "search" in req:
        tool_calls.append({"tool": "web.search", "payload": {"query": state["user_request"]}})
    else:
        # Default action
        tool_calls.append({"tool": "gmail.search", "payload": {"query": "is:unread"}})
        
    if state.get("workflow_step_id"):
        async with AsyncSessionLocal() as db:
            event = WorkflowEvent(
                workflow_step_id=uuid.UUID(state["workflow_step_id"]),
                event_type="agent_decision",
                payload={"tool_calls": tool_calls}
            )
            db.add(event)
            await db.commit()
        
    return {"tool_calls": tool_calls}

async def check_policy(state: CoordinatorState):
    """Checks if tool calls require human approval based on ToolPolicy (mocked)"""
    # For MVP: let's pretend "gmail.send" requires approval, "web.search" does not
    # In a real app we would query ToolPolicy table
    needs_approval = False
    risk = "LOW"
    
    for tc in state.get("tool_calls", []):
        tool_name = tc["tool"]
        if tool_name == "gmail.send":
            needs_approval = True
            risk = "HIGH"
            tool_call = tc
            break

    if needs_approval:
        async with AsyncSessionLocal() as db:
            agent_uuid = uuid.UUID(state["coordinator_agent_id"]) if state.get("coordinator_agent_id") else uuid.uuid4()
            approval = PendingApproval(
                workspace_id=uuid.UUID(state["workspace_id"]),
                workflow_run_id=uuid.UUID(state["workflow_run_id"]),
                tool_call_id=str(uuid.uuid4()), # idempotency_key equivalent
                agent_id=agent_uuid,
                risk_level=risk,
                action_type=tool_name,
                payload_preview=tool_call["payload"],
                status="pending"
            )
            db.add(approval)
            
            if state.get("workflow_step_id"):
                event = WorkflowEvent(
                    workflow_step_id=uuid.UUID(state["workflow_step_id"]),
                    event_type="paused_for_approval",
                    payload={"approval_id": str(approval.id), "tool": tool_name}
                )
                db.add(event)
                
            await db.commit()
            await db.refresh(approval)
            
            return {
                "status": "paused_for_approval",
                "pending_approval_id": str(approval.id)
            }
            
    return {"status": "running"}

def route_after_policy(state: CoordinatorState):
    if state["status"] == "paused_for_approval":
        return "pause"
    return "execute_tools"

async def execute_tools(state: CoordinatorState):
    """Executes the tools"""
    results = list(state.get("results", []))
    
    for tc in state.get("tool_calls", []):
        tool = tc["tool"]
        try:
            # Delegate execution to the ToolGateway
            tool_result = await ToolGateway.execute(tool, tc.get("payload", {}))
        except Exception as e:
            tool_result = f"Error executing tool {tool}: {str(e)}"
            
        results.append({
            "tool": tool, 
            "result": tool_result
        })
            
    if state.get("workflow_step_id"):
        async with AsyncSessionLocal() as db:
            step = await db.get(WorkflowStep, uuid.UUID(state["workflow_step_id"]))
            if step:
                step.status = "completed"
                event = WorkflowEvent(
                    workflow_step_id=step.id,
                    event_type="tools_executed",
                    payload={"results": results}
                )
                db.add(event)
            await db.commit()
            
    return {"results": results, "status": "completed"}

# Build Graph
builder = StateGraph(CoordinatorState)

builder.add_node("start", start_run)
builder.add_node("agent", agent_execute)
builder.add_node("policy", check_policy)
builder.add_node("execute", execute_tools)
builder.add_node("pause", lambda s: {"status": "paused_for_approval"})

builder.set_entry_point("start")
builder.add_edge("start", "agent")
builder.add_edge("agent", "policy")
builder.add_conditional_edges("policy", route_after_policy, {
    "pause": "pause",
    "execute_tools": "execute"
})
builder.add_edge("pause", END)
builder.add_edge("execute", END)

coordinator_app = builder.compile()
