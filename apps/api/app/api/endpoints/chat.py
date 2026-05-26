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
from apps.api.app.db.models.workflow import WorkflowRun, WorkflowEvent
from apps.api.app.tasks.worker import run_coordinator_task
from apps.api.app.core.statuses import WorkflowRunStatus, WorkflowSource
from fastapi.responses import StreamingResponse
import asyncio
import json

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
        content=req.content
    )
    db.add(user_msg)
    await db.flush()
    
    # Removed explicit Task creation for chat messages
    
    # Initialize Workflow
    run = WorkflowRun(
        workspace_id=workspace.id,
        task_id=None,
        conversation_id=convo.id,
        source=WorkflowSource.chat,
        status=WorkflowRunStatus.queued,
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

@router.get("/conversations/{conversation_id}/stream")
async def stream_conversation_events(
    conversation_id: str,
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    """
    Server-Sent Events (SSE) endpoint to stream real-time updates for a conversation.
    """
    result = await db.execute(select(Conversation).where(Conversation.id == uuid.UUID(conversation_id)))
    convo = result.scalar_one_or_none()
    
    if not convo or convo.workspace_id != workspace.id:
        raise HTTPException(status_code=404, detail="Conversation not found")

    async def event_generator():
        # In a real production system, this would subscribe to Redis Pub/Sub channel
        # e.g., using a global Redis connection: `await redis.subscribe(f"convo:{conversation_id}")`
        # For the MVP/SaaS foundation, we will simulate the SSE subscription via DB polling
        # or just sending a ping. Ideally, we yield events from Redis.
        
        last_event_id = 0
        try:
            while True:
                # Polling DB for new messages/events for this conversation
                # Production: Replace with Redis PubSub!
                from apps.api.app.db.database import AsyncSessionLocal
                async with AsyncSessionLocal() as session:
                    # Get newest workflow runs for this convo
                    run_res = await session.execute(
                        select(WorkflowRun)
                        .where(WorkflowRun.conversation_id == convo.id)
                        .order_by(WorkflowRun.created_at.desc())
                        .limit(1)
                    )
                    latest_run = run_res.scalar_one_or_none()
                    
                    if latest_run:
                        # Fetch new WorkflowEvents
                        events_res = await session.execute(
                            select(WorkflowEvent)
                            .where(
                                WorkflowEvent.workflow_run_id == latest_run.id,
                                WorkflowEvent.sequence_number > last_event_id
                            )
                            .order_by(WorkflowEvent.sequence_number.asc())
                        )
                        new_events = events_res.scalars().all()
                        for ev in new_events:
                            data = json.dumps({
                                "type": ev.event_type,
                                "payload": ev.payload,
                                "run_status": latest_run.status
                            })
                            yield f"data: {data}\n\n"
                            last_event_id = ev.sequence_number
                
                await asyncio.sleep(2) # Polling interval
        except asyncio.CancelledError:
            # Client disconnected
            pass

    return StreamingResponse(event_generator(), media_type="text/event-stream")
