from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from pydantic import BaseModel
import uuid

from apps.api.app.db.database import get_db
from apps.api.app.db.models.core import User, Workspace
from apps.api.app.db.models.chat import Conversation, Message, MessageAttachment
from apps.api.app.api.deps import get_current_workspace, get_current_user
from apps.api.app.db.models.workflow import WorkflowRun
from apps.api.app.tasks.worker import run_coordinator_task

router = APIRouter()

class SendMessageRequest(BaseModel):
    content: str

class ConversationResponse(BaseModel):
    id: str
    title: str
    conversation_type: str
    agent_id: str | None
    team_id: str | None
    created_at: str

class MessageResponse(BaseModel):
    id: str
    sender_type: str
    content: str | None
    created_at: str

@router.get("/conversations", response_model=List[ConversationResponse])
async def get_conversations(
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Conversation)
        .where(Conversation.workspace_id == workspace.id)
        .order_by(Conversation.updated_at.desc())
    )
    convos = result.scalars().all()
    
    return [
        ConversationResponse(
            id=str(c.id),
            title=c.title or "New Chat",
            conversation_type=c.conversation_type,
            agent_id=str(c.agent_id) if c.agent_id else None,
            team_id=str(c.team_id) if c.team_id else None,
            created_at=c.created_at.isoformat() if c.created_at else ""
        ) for c in convos
    ]

@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    conversation_id: str,
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Conversation).where(Conversation.id == uuid.UUID(conversation_id)))
    convo = result.scalar_one_or_none()
    
    if not convo or convo.workspace_id != workspace.id:
        raise HTTPException(status_code=404, detail="Conversation not found")
        
    messages_result = await db.execute(
        select(Message)
        .where(Message.conversation_id == convo.id)
        .order_by(Message.created_at.asc())
    )
    messages = messages_result.scalars().all()
    
    return [
        MessageResponse(
            id=str(m.id),
            sender_type=m.sender_type,
            content=m.content,
            created_at=m.created_at.isoformat() if m.created_at else ""
        ) for m in messages
    ]

@router.post("/conversations/{conversation_id}/messages", response_model=MessageResponse)
async def send_message(
    conversation_id: str,
    req: SendMessageRequest,
    workspace: Workspace = Depends(get_current_workspace),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Conversation).where(Conversation.id == uuid.UUID(conversation_id)))
    convo = result.scalar_one_or_none()
    
    if not convo or convo.workspace_id != workspace.id:
        raise HTTPException(status_code=404, detail="Conversation not found")
        
    # Save User Message
    user_msg = Message(
        conversation_id=convo.id,
        sender_type="user",
        sender_id=current_user.id,
        content=req.content
    )
    db.add(user_msg)
    await db.flush()
    
    # Initialize Workflow
    run = WorkflowRun(
        workspace_id=workspace.id,
        name=f"Chat Workflow: {req.content[:20]}...",
        status="pending",
        created_by=current_user.id
    )
    db.add(run)
    await db.commit()
    await db.refresh(run)
    
    # Send to Celery
    initial_state = {
        "workflow_run_id": str(run.id),
        "workspace_id": str(workspace.id),
        "user_id": str(current_user.id),
        "user_request": req.content,
        "current_agent_id": str(convo.agent_id) if convo.agent_id else None, # Route to the agent in the chat
        "status": "running",
        "conversation_id": str(convo.id)
    }
    
    run_coordinator_task.delay(initial_state)
    
    return MessageResponse(
        id=str(user_msg.id),
        sender_type=user_msg.sender_type,
        content=user_msg.content,
        created_at=user_msg.created_at.isoformat() if user_msg.created_at else ""
    )
