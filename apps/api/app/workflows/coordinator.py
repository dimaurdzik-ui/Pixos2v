import uuid
import asyncio
import json
from typing import TypedDict, Any, Optional
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg_pool import AsyncConnectionPool
import os
from apps.api.app.db.database import AsyncSessionLocal
from apps.api.app.db.models.workflow import WorkflowStep, WorkflowEvent, WorkflowRun
from apps.api.app.db.models.policy import PendingApproval
from apps.api.app.db.models.billing import CreditBalance, UsageRecord
from apps.api.app.services.tools.gateway import ToolGateway

class CoordinatorState(TypedDict):
    workflow_run_id: str
    task_id: str
    workspace_id: str
    user_id: str
    conversation_id: Optional[str]
    coordinator_agent_id: str
    current_agent_id: str
    workflow_step_id: Optional[str]
    user_request: str
    current_step: int
    tool_calls: list[dict] # e.g. [{"tool": "gmail.send", "payload": {...}}]
    results: list[Any]
    messages: list[dict] # LLM conversation history
    status: str # "running", "paused_for_approval", "completed", "failed"
    pending_approval_id: Optional[str] # if paused
    total_cost: float
    artifact_content: str

async def start_run(state: CoordinatorState):
    """Initializes the workflow step in DB"""
    async with AsyncSessionLocal() as db:
        run = await db.get(WorkflowRun, uuid.UUID(state["workflow_run_id"]))
        if run:
            run.status = "running"
            
        step = WorkflowStep(
            workflow_run_id=uuid.UUID(state["workflow_run_id"]),
            step_order=state.get("current_step", 0),
            action="init",
            agent_id=uuid.UUID(state["current_agent_id"]) if state.get("current_agent_id") else None,
            status="running"
        )
        db.add(step)
        await db.commit()
        await db.refresh(step)
        
    messages = state.get("messages", [])
    if not messages:
        messages = [
            {"role": "system", "content": "You are Pixos System Coordinator. Use tools to fulfill the user request. Once fulfilled, do not call any more tools."},
            {"role": "user", "content": state.get("user_request", "")}
        ]
        
    return {"status": "running", "workflow_step_id": str(step.id), "messages": messages}

async def agent_execute(state: CoordinatorState):
    """Real Agent Coordinator using LiteLLM and ToolRegistry schemas"""
    from apps.api.app.core.config import settings
    from apps.api.app.services.tools.registry import ToolRegistry
    import litellm
    
    tool_calls = []
    messages = list(state.get("messages", []))
    
    # Check if we should run real LLM or mock
    if settings.OPENAI_API_KEY:
        schemas = ToolRegistry.get_all_schemas()
        
        # 1. DYNAMIC AGENT DISCOVERY
        # Fetch active agents in the workspace to allow delegation
        async with AsyncSessionLocal() as db:
            from apps.api.app.db.models.agents import Agent
            from sqlalchemy import select
            
            result = await db.execute(
                select(Agent).where(
                    Agent.workspace_id == uuid.UUID(state["workspace_id"]),
                    Agent.status == "active",
                    Agent.is_coordinator == False
                )
            )
            available_agents = result.scalars().all()
            
            for agent in available_agents:
                clean_name = "".join(c if c.isalnum() else "_" for c in agent.name.lower())
                agent_tool = {
                    "type": "function",
                    "function": {
                        "name": f"delegate_to_agent_{str(agent.id)}",
                        "description": f"Delegate a task to {agent.name}. Role: {agent.role}. {agent.description or ''}. Use this when you need specialized help from this team member.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "task": {
                                    "type": "string",
                                    "description": "Detailed instructions on what you want this agent to do."
                                }
                            },
                            "required": ["task"]
                        }
                    }
                }
                schemas.append(agent_tool)
        
        try:
            response = await litellm.acompletion(
                model="gpt-4o",
                messages=messages,
                tools=schemas,
                tool_choice="auto"
            )
            message = response.choices[0].message
            
            # Calculate real LLM cost
            try:
                cost = litellm.completion_cost(completion_response=response)
                # 1 cent = 1 credit (e.g. $0.001 = 0.1 credits)
                added_cost = cost * 100 
                state["total_cost"] = state.get("total_cost", 0) + added_cost
            except Exception as e:
                print(f"Cost calculation error: {e}")
            
            # Append assistant message to state
            assistant_msg = {"role": "assistant"}
            if message.content:
                assistant_msg["content"] = message.content
            if hasattr(message, "tool_calls") and message.tool_calls:
                assistant_msg["tool_calls"] = []
                for tc in message.tool_calls:
                    assistant_msg["tool_calls"].append({
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    })
                    tool_calls.append({
                        "id": tc.id,
                        "tool": tc.function.name,
                        "payload": json.loads(tc.function.arguments)
                    })
            messages.append(assistant_msg)
        except Exception as e:
            print(f"LLM Error: {e}")
            tool_calls = []
    else:
        # MOCK FALLBACK
        request = state.get("user_request", "").lower()
        if not state.get("results"):
            if "email" in request:
                tool_calls.append({"id": "call_1", "tool": "gmail.send", "payload": {"to": "test@example.com", "subject": "Test", "body": request}})
            elif "search" in request:
                tool_calls.append({"id": "call_1", "tool": "web.search", "payload": {"query": request}})
            else:
                tool_calls.append({"id": "call_1", "tool": "gmail.search", "payload": {"query": "is:unread"}})
                
        assistant_msg = {"role": "assistant", "content": None, "tool_calls": [{"id": tc["id"], "type": "function", "function": {"name": tc["tool"], "arguments": json.dumps(tc["payload"])}} for tc in tool_calls]}
        if tool_calls:
            messages.append(assistant_msg)
    
    if state.get("workflow_step_id"):
        async with AsyncSessionLocal() as db:
            event = WorkflowEvent(
                workflow_run_id=uuid.UUID(state["workflow_run_id"]),
                workflow_step_id=uuid.UUID(state["workflow_step_id"]),
                event_type="agent_decision",
                payload={"tool_calls": tool_calls}
            )
            db.add(event)
            await db.commit()
            
    return {"tool_calls": tool_calls, "messages": messages}

def route_after_execute(state: CoordinatorState):
    return "agent"

async def execute_tools(state: CoordinatorState):
    """Executes the tools"""
    results = list(state.get("results", []))
    messages = list(state.get("messages", []))
    
    for tc in state.get("tool_calls", []):
        tool = tc["tool"]
        tool_call_id = tc.get("id", "unknown")
        
        # Build context for ToolGateway
        context = {
            "workspace_id": state.get("workspace_id"),
            "workflow_run_id": state.get("workflow_run_id"),
            "agent_id": state.get("current_agent_id"),
            "workflow_step_id": state.get("workflow_step_id"),
            "user_id": state.get("user_id"),
            "tool_call_id": tool_call_id
        }
        
        try:
            # 2. SUB-AGENT EXECUTION
            if tool.startswith("delegate_to_agent_"):
                agent_id_str = tool.replace("delegate_to_agent_", "")
                
                async with AsyncSessionLocal() as db:
                    from apps.api.app.db.models.agents import Agent
                    agent = await db.get(Agent, uuid.UUID(agent_id_str))
                    
                    if not agent:
                        tool_result = f"Error: Agent with ID {agent_id_str} not found or unavailable."
                    else:
                        # Log delegation event
                        if state.get("workflow_step_id"):
                            event = WorkflowEvent(
                                workflow_run_id=uuid.UUID(state["workflow_run_id"]),
                                workflow_step_id=uuid.UUID(state["workflow_step_id"]),
                                event_type="agent_delegation",
                                payload={"agent_id": str(agent.id), "agent_name": agent.name, "task": tc.get("payload", {}).get("task")}
                            )
                            db.add(event)
                            await db.commit()
                            
                        # Execute Sub-Agent
                        tool_result = await execute_sub_agent(agent, tc.get("payload", {}).get("task", ""), messages, state)
            else:
                # Delegate execution to the ToolGateway
                tool_result = await ToolGateway.execute(tool, tc.get("payload", {}), context)
        except Exception as e:
            from langgraph.errors import NodeInterrupt
            if isinstance(e, NodeInterrupt):
                raise
            tool_result = f"Error executing tool {tool}: {str(e)}"
            
        results.append({
            "tool": tool, 
            "result": tool_result
        })
        
        # Append tool output to messages
        messages.append({
            "role": "tool",
            "name": tool,
            "tool_call_id": tool_call_id,
            "content": str(tool_result)
        })
            
    if state.get("workflow_step_id"):
        async with AsyncSessionLocal() as db:
            step = await db.get(WorkflowStep, uuid.UUID(state["workflow_step_id"]))
            if step:
                step.status = "completed"
                event = WorkflowEvent(
                    workflow_run_id=uuid.UUID(state["workflow_run_id"]),
                    workflow_step_id=step.id,
                    event_type="tools_executed",
                    payload={"results": results}
                )
                db.add(event)
            await db.commit()
            
    # If no tool calls were made initially in agent_execute
    if not state.get("tool_calls", []) and not state.get("sub_agent_tool_calls", []):
        async with AsyncSessionLocal() as db:
            run = await db.get(WorkflowRun, uuid.UUID(state["workflow_run_id"]))
            if run:
                run.status = "completed"
            await db.commit()
        return {"status": "completed"}
        
    return {"results": results, "messages": messages, "tool_calls": [], "status": "running"}

async def execute_sub_agent(agent, task: str, coordinator_history: list[dict], state: CoordinatorState) -> str:
    """Executes a sub-agent loop for delegation"""
    from apps.api.app.core.config import settings
    from apps.api.app.services.tools.registry import ToolRegistry
    from apps.api.app.services.tools.gateway import ToolGateway
    import litellm
    
    if not settings.OPENAI_API_KEY:
        return f"Mock Sub-Agent {agent.name} executed task: {task}"
        
    # Build context for sub-agent
    sub_messages = [
        {"role": "system", "content": agent.system_prompt or f"You are {agent.name}, a {agent.role}. Fulfill the delegated task."}
    ]
    
    # Optionally append summary of previous messages or the exact task
    sub_messages.append({"role": "user", "content": f"Delegated Task from Coordinator: {task}"})
    
    # Load sub-agent tools
    schemas = []
    agent_tools = agent.tools or []
    all_schemas = ToolRegistry.get_all_schemas()
    for s in all_schemas:
        if s["function"]["name"] in agent_tools:
            schemas.append(s)
            
    try:
        # One-shot or loop? MVP: One-shot LLM call with tools
        response = await litellm.acompletion(
            model=agent.model or "gpt-4o",
            messages=sub_messages,
            tools=schemas if schemas else None,
            tool_choice="auto" if schemas else None
        )
        message = response.choices[0].message
        
        # Calculate real LLM cost for sub-agent
        try:
            cost = litellm.completion_cost(completion_response=response)
            added_cost = cost * 100 
            state["total_cost"] = state.get("total_cost", 0) + added_cost
        except Exception as e:
            print(f"Cost calculation error: {e}")
        
        # If the sub-agent needs to call tools itself, we can execute them here
        if hasattr(message, "tool_calls") and message.tool_calls:
            # INSTEAD OF EXECUTING SYNCHRONOUSLY, WE YIELD TO PARENT POLICY!
            sub_tools = []
            for tc in message.tool_calls:
                tool_name = tc.function.name
                payload = json.loads(tc.function.arguments)
                sub_tools.append({
                    "id": tc.id,
                    "tool": tool_name,
                    "payload": payload
                })
            
            # Store them in the state so `execute_tools` can pick them up
            state["sub_agent_tool_calls"] = state.get("sub_agent_tool_calls", []) + sub_tools
            return f"Agent {agent.name} has queued tools for execution."
            
        return f"Agent {agent.name} says: {message.content}"
    except Exception as e:
        return f"Error executing Sub-Agent {agent.name}: {e}"

# Build Graph
builder = StateGraph(CoordinatorState)

builder.add_node("start", start_run)
builder.add_node("agent", agent_execute)
builder.add_node("execute", execute_tools)

def route_after_agent(state: CoordinatorState):
    if not state.get("tool_calls"):
        return "END"
    return "execute"

def route_after_execute(state: CoordinatorState):
    if state.get("status") == "completed":
        return "END"
    return "agent"

builder.set_entry_point("start")
builder.add_edge("start", "agent")
builder.add_conditional_edges("agent", route_after_agent, {
    "execute": "execute",
    "END": END
})
builder.add_conditional_edges("execute", route_after_execute, {
    "agent": "agent",
    "END": END
})

# Create a connection pool for the checkpointer
DATABASE_URL = os.environ.get(
    "DATABASE_URL", 
    "postgresql+asyncpg://postgres:postgres@localhost:5432/pixos"
)
# AsyncPostgresSaver expects psycopg connection string (postgresql:// not postgresql+asyncpg://)
pg_url = DATABASE_URL.replace("+asyncpg", "")
if pg_url.startswith("postgres://"):
    pg_url = pg_url.replace("postgres://", "postgresql://", 1)

# We initialize the checkpointer in a lazy way or just create the pool here.
# Since this module might be imported before the loop runs, we use a global pool 
# and initialize the saver asynchronously. But LangGraph compile() allows passing 
# the checkpointer directly. Let's create a global pool.
pool = AsyncConnectionPool(
    conninfo=pg_url,
    max_size=20,
    kwargs={"autocommit": True, "prepare_threshold": 0}
)

checkpointer = AsyncPostgresSaver(pool)

# Note: AsyncPostgresSaver.setup() needs to be called somewhere to create tables.
# We assume it's called during app startup.

coordinator_app = builder.compile(checkpointer=checkpointer)
