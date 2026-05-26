import uuid
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional

from apps.api.app.db.database import get_db
from apps.api.app.db.models.agents import Agent
from apps.api.app.db.models.core import Workspace, User
from apps.api.app.db.models.chat import Conversation, Message
from apps.api.app.db.models.workflow import Task, WorkflowRun
from apps.api.app.api.deps import get_current_workspace, get_current_user, require_permission

router = APIRouter()

class AgentCreate(BaseModel):
    name: str
    role: str
    job_title: Optional[str] = None
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    model_name: Optional[str] = "gpt-4o"
    autonomy_level: Optional[str] = "balanced"
    safety_level: Optional[str] = "high"
    status: Optional[str] = "active"
    team_id: Optional[str] = None
    tools: Optional[list[str]] = []

class AgentUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    job_title: Optional[str] = None
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    model_name: Optional[str] = None
    autonomy_level: Optional[str] = None
    safety_level: Optional[str] = None
    status: Optional[str] = None
    team_id: Optional[str] = None
    tools: Optional[list[str]] = None

class AgentTaskCreate(BaseModel):
    description: str

class AgentChatCreate(BaseModel):
    conversation_id: Optional[str] = None
    message: str

@router.get("")
async def get_agents(
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Agent).where(Agent.workspace_id == workspace.id).order_by(Agent.created_at)
    )
    agents = result.scalars().all()
    
    return [
        {
            "id": str(a.id),
            "name": a.name,
            "role": a.role,
            "job_title": a.job_title,
            "description": a.description,
            "is_coordinator": a.is_coordinator,
            "model_name": a.model,
            "autonomy_level": a.autonomy_level,
            "safety_level": a.safety_level,
            "status": a.status,
            "team_id": str(a.team_id) if a.team_id else None,
            "tools": a.tools or [],
            "system_prompt": a.system_prompt,
            "created_at": a.created_at.isoformat() if a.created_at else None
        }
        for a in agents
    ]

@router.post("", response_model=dict)
async def create_agent(
    agent_in: AgentCreate,
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db),
    _ = Depends(require_permission("manage_agents"))
):
    team_id = uuid.UUID(agent_in.team_id) if agent_in.team_id else None

    new_agent = Agent(
        workspace_id=workspace.id,
        name=agent_in.name,
        role=agent_in.role,
        job_title=agent_in.job_title,
        description=agent_in.description,
        system_prompt=agent_in.system_prompt,
        model=agent_in.model_name,
        autonomy_level=agent_in.autonomy_level,
        safety_level=agent_in.safety_level,
        status=agent_in.status,
        team_id=team_id,
        tools=agent_in.tools,
        is_coordinator=False
    )
    db.add(new_agent)
    await db.commit()
    await db.refresh(new_agent)
    
    return {
        "id": str(new_agent.id),
        "name": new_agent.name,
        "description": new_agent.description,
        "is_coordinator": new_agent.is_coordinator,
        "tools": new_agent.tools
    }

@router.put("/{agent_id}", response_model=dict)
async def update_agent(
    agent_id: str,
    agent_in: AgentUpdate,
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db),
    _ = Depends(require_permission("manage_agents"))
):
    try:
        aid = uuid.UUID(agent_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid agent ID")
        
    agent = await db.get(Agent, aid)
    if not agent or agent.workspace_id != workspace.id:
        raise HTTPException(status_code=404, detail="Agent not found")
        
    update_data = agent_in.model_dump(exclude_unset=True)
    if "model_name" in update_data:
        update_data["model"] = update_data.pop("model_name")
    if "team_id" in update_data:
        update_data["team_id"] = uuid.UUID(update_data["team_id"]) if update_data["team_id"] else None
        
    for field, value in update_data.items():
        setattr(agent, field, value)
        
    await db.commit()
    await db.refresh(agent)
    
    return {
        "id": str(agent.id),
        "status": "updated"
    }

@router.delete("/{agent_id}")
async def delete_agent(
    agent_id: str,
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db),
    _ = Depends(require_permission("manage_agents"))
):
    try:
        aid = uuid.UUID(agent_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid agent ID")
        
    agent = await db.get(Agent, aid)
    if not agent or agent.workspace_id != workspace.id:
        raise HTTPException(status_code=404, detail="Agent not found")
        
    if agent.is_coordinator:
        raise HTTPException(status_code=400, detail="Cannot delete the System Coordinator agent")
        
    await db.delete(agent)
    await db.commit()
    return {"status": "success"}

@router.post("/{agent_id}/tasks", response_model=dict)
async def create_agent_task(
    agent_id: str,
    task_in: AgentTaskCreate,
    workspace: Workspace = Depends(get_current_workspace),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        aid = uuid.UUID(agent_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid agent ID")
        
    agent = await db.get(Agent, aid)
    if not agent or agent.workspace_id != workspace.id:
        raise HTTPException(status_code=404, detail="Agent not found")
        
    task = Task(
        workspace_id=workspace.id,
        created_by=current_user.id,
        description=task_in.description,
        status="pending"
    )
    db.add(task)
    await db.flush()
    
    run = WorkflowRun(
        workspace_id=workspace.id,
        task_id=task.id,
        status="started"
    )
    db.add(run)
    await db.commit()
    
    # We could trigger the workflow here asynchronously
    # For now, we just return it
    
    return {
        "task_id": str(task.id),
        "workflow_run_id": str(run.id),
        "status": "started"
    }

@router.post("/{agent_id}/chat", response_model=dict)
async def create_agent_chat(
    agent_id: str,
    chat_in: AgentChatCreate,
    workspace: Workspace = Depends(get_current_workspace),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        aid = uuid.UUID(agent_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid agent ID")
        
    agent = await db.get(Agent, aid)
    if not agent or agent.workspace_id != workspace.id:
        raise HTTPException(status_code=404, detail="Agent not found")
        
    # Get or create conversation
    if chat_in.conversation_id:
        conv_id = uuid.UUID(chat_in.conversation_id)
        conv = await db.get(Conversation, conv_id)
        if not conv or conv.workspace_id != workspace.id:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        conv = Conversation(
            workspace_id=workspace.id,
            agent_id=aid,
            title=chat_in.message[:50]
        )
        db.add(conv)
        await db.flush()
        
    # Add user message
    user_msg = Message(
        conversation_id=conv.id,
        sender_type="user",
        content=chat_in.message
    )
    db.add(user_msg)
    await db.commit()
    
    # In a real implementation, we would spawn an async LangGraph run here
    # and maybe return a run_id. For now, we'll invoke synchronously to test MVP
    
    # Let's import the coordinator graph
    from apps.api.app.workflows.coordinator import coordinator_app
    
    # Fetch history
    from sqlalchemy import select
    result = await db.execute(
        select(Message).where(Message.conversation_id == conv.id).order_by(Message.created_at)
    )
    history = result.scalars().all()
    
    langgraph_messages = []
    if agent.system_prompt:
        langgraph_messages.append({"role": "system", "content": agent.system_prompt})
        
    for m in history:
        if m.sender_type == "user":
            langgraph_messages.append({"role": "user", "content": m.content})
        elif m.sender_type == "agent":
            langgraph_messages.append({"role": "assistant", "content": m.content})
        elif m.sender_type == "tool":
            pass # handling tools in history can be complex, skip for now
            
    # Create a Task and WorkflowRun for the chat interaction
    chat_task = Task(
        workspace_id=workspace.id,
        created_by=current_user.id,
        description=f"Chat interaction: {chat_in.message[:50]}...",
        status="running"
    )
    db.add(chat_task)
    await db.flush()
    
    chat_run = WorkflowRun(
        workspace_id=workspace.id,
        task_id=chat_task.id,
        status="started"
    )
    db.add(chat_run)
    await db.commit()
    
    initial_state = {
        "workflow_run_id": str(chat_run.id),
        "task_id": str(chat_task.id),
        "workspace_id": str(workspace.id),
        "user_id": str(current_user.id),
        "current_agent_id": str(agent.id),
        "user_request": chat_in.message,
        "messages": langgraph_messages,
        "status": "running",
        "results": [],
        "tool_calls": []
    }
    
    final_state = await coordinator_app.ainvoke(initial_state, config={"configurable": {"thread_id": str(conv.id)}})
    
    # Extract agent's reply
    reply_content = None
    new_tool_calls = []
    
    # Look at the last message
    if final_state["messages"]:
        last_msg = final_state["messages"][-1]
        if last_msg.get("role") == "assistant":
            reply_content = last_msg.get("content")
            if "tool_calls" in last_msg and last_msg["tool_calls"]:
                # the tool calls were saved in the final_state tool_calls
                new_tool_calls = final_state.get("tool_calls", [])
                
    if not reply_content and not new_tool_calls:
        reply_content = "I'm not sure how to respond to that."
        
    agent_msg = Message(
        conversation_id=conv.id,
        sender_type="agent",
        content=reply_content,
        tool_calls=new_tool_calls if new_tool_calls else None
    )
    db.add(agent_msg)
    await db.commit()
    
    return {
        "conversation_id": str(conv.id),
        "message": reply_content,
        "tool_calls": new_tool_calls,
        "status": final_state.get("status")
    }
