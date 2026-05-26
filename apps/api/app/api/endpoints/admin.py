from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime, timezone, timedelta

from apps.api.app.db.database import get_db
from apps.api.app.db.models.core import User, Workspace, AuditLog, WorkspaceMember
from apps.api.app.db.models.agents import Agent
from apps.api.app.db.models.workflow import WorkflowRun
from apps.api.app.db.models.system import SystemConfig
from apps.api.app.db.models.billing import StripeEvent, CreditBalance
from apps.api.app.db.models.policy import PendingApproval
from apps.api.app.api.deps import require_super_admin
from apps.api.app.core.encryption import encrypt_value

router = APIRouter()

# --- SYSTEM CONFIG ---
class SystemConfigUpdate(BaseModel):
    key_name: str
    value: str

class SystemConfigResponse(BaseModel):
    key_name: str
    is_set: bool
    is_active: bool

@router.get("/system-config", response_model=List[SystemConfigResponse])
async def get_system_config(
    db: AsyncSession = Depends(get_db),
    _ = Depends(require_super_admin)
):
    result = await db.execute(select(SystemConfig))
    configs = result.scalars().all()
    
    return [
        SystemConfigResponse(
            key_name=c.key_name,
            is_set=bool(c.encrypted_value),
            is_active=c.is_active
        ) for c in configs
    ]

@router.post("/system-config")
async def update_system_config(
    config: SystemConfigUpdate,
    current_user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(SystemConfig).where(SystemConfig.key_name == config.key_name))
    db_config = result.scalar_one_or_none()
    
    encrypted = encrypt_value(config.value) if config.value else None
    
    if db_config:
        db_config.encrypted_value = encrypted
        db_config.updated_by = current_user.id
    else:
        db_config = SystemConfig(
            key_name=config.key_name,
            encrypted_value=encrypted,
            updated_by=current_user.id
        )
        db.add(db_config)
        
    # Create Audit Log
    audit = AuditLog(
        user_id=current_user.id,
        action="system_config_updated",
        target_id=config.key_name,
        details={"key": config.key_name}
    )
    db.add(audit)
        
    await db.commit()
    return {"status": "success"}

# --- OVERVIEW ---
class AdminOverview(BaseModel):
    total_workspaces: int
    total_users: int
    total_agents: int
    running_workflows: int
    failed_workflows: int
    pending_approvals: int
    total_credits: int
    llm_spend_today: int
    stripe_revenue_today: int
    provider_health: str
    celery_status: str
    redis_status: str
    database: str

@router.get("/overview", response_model=AdminOverview)
async def get_overview(
    db: AsyncSession = Depends(get_db),
    _ = Depends(require_super_admin)
):
    workspaces_count = await db.scalar(select(func.count()).select_from(Workspace))
    users_count = await db.scalar(select(func.count()).select_from(User))
    agents_count = await db.scalar(select(func.count()).select_from(Agent))
    
    running_workflows = await db.scalar(
        select(func.count()).select_from(WorkflowRun).where(WorkflowRun.status == "running")
    )
    failed_workflows = await db.scalar(
        select(func.count()).select_from(WorkflowRun).where(WorkflowRun.status == "failed")
    )
    
    pending_approvals = await db.scalar(
        select(func.count()).select_from(PendingApproval).where(PendingApproval.status == "pending")
    )
    
    total_credits = await db.scalar(
        select(func.sum(CreditBalance.balance))
    )
    
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    
    llm_spend_today = await db.scalar(
        select(func.sum(WorkflowRun.total_cost)).where(WorkflowRun.created_at >= today)
    )
    
    stripe_revenue_today = await db.scalar(
        select(func.sum(StripeEvent.amount_total)).where(
            StripeEvent.created_at >= today,
            StripeEvent.event_type == 'checkout.session.completed'
        )
    )
    
    # Simple Ping Checks
    database_status = "healthy"
    redis_status = "healthy" # Assume healthy for MVP, or ping Redis
    celery_status = "healthy" # Assume healthy for MVP, or check worker
    provider_health = "healthy" # Check OpenAI/Anthropic status
    
    return AdminOverview(
        total_workspaces=workspaces_count or 0,
        total_users=users_count or 0,
        total_agents=agents_count or 0,
        running_workflows=running_workflows or 0,
        failed_workflows=failed_workflows or 0,
        pending_approvals=pending_approvals or 0,
        total_credits=total_credits or 0,
        llm_spend_today=llm_spend_today or 0,
        stripe_revenue_today=stripe_revenue_today or 0,
        provider_health=provider_health,
        celery_status=celery_status,
        redis_status=redis_status,
        database=database_status
    )

# --- WORKSPACES ---
class AdminWorkspaceList(BaseModel):
    id: str
    name: str
    is_active: bool
    created_at: datetime
    users_count: int

@router.get("/workspaces", response_model=List[AdminWorkspaceList])
async def list_workspaces(
    db: AsyncSession = Depends(get_db),
    _ = Depends(require_super_admin)
):
    # For now, simplistic list
    result = await db.execute(
        select(Workspace, func.count(WorkspaceMember.id))
        .outerjoin(WorkspaceMember, WorkspaceMember.workspace_id == Workspace.id)
        .group_by(Workspace.id)
        .order_by(desc(Workspace.created_at))
    )
    rows = result.all()
    
    return [
        AdminWorkspaceList(
            id=str(w.id),
            name=w.name,
            is_active=w.is_active,
            created_at=w.created_at,
            users_count=count
        ) for w, count in rows
    ]

@router.post("/workspaces/{id}/disable")
async def disable_workspace(
    id: str,
    current_user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Workspace).where(Workspace.id == id))
    ws = result.scalar_one_or_none()
    if not ws:
        raise HTTPException(404, "Not found")
    
    ws.is_active = False
    audit = AuditLog(
        user_id=current_user.id, action="workspace_disabled", target_id=str(ws.id)
    )
    db.add(audit)
    await db.commit()
    return {"status": "success"}

@router.post("/workspaces/{id}/enable")
async def enable_workspace(
    id: str,
    current_user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Workspace).where(Workspace.id == id))
    ws = result.scalar_one_or_none()
    if not ws:
        raise HTTPException(404, "Not found")
    
    ws.is_active = True
    audit = AuditLog(
        user_id=current_user.id, action="workspace_enabled", target_id=str(ws.id)
    )
    db.add(audit)
    await db.commit()
    return {"status": "success"}

# --- USERS ---
class AdminUserList(BaseModel):
    id: str
    email: str
    full_name: Optional[str]
    is_active: bool
    is_super_admin: bool
    created_at: datetime

@router.get("/users", response_model=List[AdminUserList])
async def list_users(
    db: AsyncSession = Depends(get_db),
    _ = Depends(require_super_admin)
):
    result = await db.execute(select(User).order_by(desc(User.created_at)))
    users = result.scalars().all()
    
    return [
        AdminUserList(
            id=str(u.id),
            email=u.email,
            full_name=u.full_name,
            is_active=u.is_active,
            is_super_admin=u.is_super_admin,
            created_at=u.created_at
        ) for u in users
    ]

# --- AUDIT LOG ---
class AdminAuditLog(BaseModel):
    id: str
    user_id: Optional[str]
    workspace_id: Optional[str]
    action: str
    target_id: Optional[str]
    details: Optional[Dict[str, Any]]
    created_at: datetime

@router.get("/audit", response_model=List[AdminAuditLog])
async def list_audit_logs(
    action: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    _ = Depends(require_super_admin)
):
    stmt = select(AuditLog).order_by(desc(AuditLog.created_at)).limit(100)
    if action:
        stmt = stmt.where(AuditLog.action == action)
        
    result = await db.execute(stmt)
    logs = result.scalars().all()
    
    return [
        AdminAuditLog(
            id=str(a.id),
            user_id=str(a.user_id) if a.user_id else None,
            workspace_id=str(a.workspace_id) if a.workspace_id else None,
            action=a.action,
            target_id=a.target_id,
            details=a.details,
            created_at=a.created_at
        ) for a in logs
    ]

# --- WORKFLOWS ---
class AdminWorkflowList(BaseModel):
    id: str
    workspace_id: str
    status: str
    error: Optional[str]
    created_at: datetime

@router.get("/workflows", response_model=List[AdminWorkflowList])
async def list_all_workflows(
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    _ = Depends(require_super_admin)
):
    stmt = select(WorkflowRun).order_by(desc(WorkflowRun.created_at)).limit(100)
    if status:
        stmt = stmt.where(WorkflowRun.status == status)
        
    result = await db.execute(stmt)
    wfs = result.scalars().all()
    
    return [
        AdminWorkflowList(
            id=str(w.id),
            workspace_id=str(w.workspace_id),
            status=w.status,
            error=w.error,
            created_at=w.created_at
        ) for w in wfs
    ]

# --- PROVIDER HEALTH ---
@router.get("/provider-health")
async def get_provider_health(
    db: AsyncSession = Depends(get_db),
    _ = Depends(require_super_admin)
):
    # Dummy implementation for now, should ping services
    return {
        "postgres": "healthy",
        "redis": "healthy",
        "celery": "healthy"
    }
