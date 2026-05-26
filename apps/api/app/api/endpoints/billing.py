import uuid
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from apps.api.app.db.database import get_db
from apps.api.app.db.models.billing import CreditBalance, UsageRecord
from apps.api.app.db.models.core import Workspace
from apps.api.app.api.deps import get_current_workspace

router = APIRouter()

@router.get("/balance")
async def get_balance(
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(CreditBalance).where(CreditBalance.workspace_id == workspace.id))
    balance = result.scalars().first()
    
    if not balance:
        return {"balance": 0}
        
    return {"balance": balance.balance}

@router.get("/history")
async def get_history(
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(UsageRecord)
        .where(UsageRecord.workspace_id == workspace.id)
        .order_by(desc(UsageRecord.created_at))
        .limit(100)
    )
    records = result.scalars().all()
    
    return [
        {
            "id": str(r.id),
            "workflow_run_id": str(r.workflow_run_id) if r.workflow_run_id else None,
            "cost": r.cost,
            "created_at": r.created_at.isoformat() if r.created_at else None
        }
        for r in records
    ]
