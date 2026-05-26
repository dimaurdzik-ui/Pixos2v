import uuid
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from apps.api.app.db.database import get_db
from apps.api.app.db.models.billing import CreditBalance, UsageRecord
from apps.api.app.db.models.core import Workspace
from apps.api.app.api.deps import get_current_workspace, require_permission
from pydantic import BaseModel
import stripe
from apps.api.app.core.config import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

router = APIRouter()

class CheckoutRequest(BaseModel):
    amount_usd: int # e.g. 10 for $10
    success_url: str
    cancel_url: str

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

@router.post("/checkout")
async def create_checkout_session(
    req: CheckoutRequest,
    workspace: Workspace = Depends(get_current_workspace),
    db: AsyncSession = Depends(get_db),
    _ = Depends(require_permission("manage_billing"))
):
    if not settings.STRIPE_SECRET_KEY:
        raise HTTPException(status_code=500, detail="Stripe is not configured on the server")
        
    try:
        # 10 USD -> 1000 Credits
        credits_amount = req.amount_usd * 100
        
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': f'{credits_amount} Pixos Credits',
                        'description': 'AI API usage credits for Pixos Agents'
                    },
                    'unit_amount': req.amount_usd * 100, # amount in cents
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=req.success_url,
            cancel_url=req.cancel_url,
            client_reference_id=str(workspace.id), # Track which workspace this belongs to
            metadata={
                "workspace_id": str(workspace.id),
                "credits": str(credits_amount)
            }
        )
        return {"url": session.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
