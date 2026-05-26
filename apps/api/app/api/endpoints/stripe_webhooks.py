import uuid
from fastapi import APIRouter, Depends, HTTPException, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import stripe

from apps.api.app.db.database import get_db
from apps.api.app.db.models.billing import CreditBalance, CreditTransaction, StripeEvent
from apps.api.app.core.config import settings

router = APIRouter()

@router.post("/webhook")
async def stripe_webhook(request: Request, stripe_signature: str = Header(None), db: AsyncSession = Depends(get_db)):
    if not settings.STRIPE_WEBHOOK_SECRET:
        raise HTTPException(status_code=500, detail="Stripe webhook secret is not configured")
        
    payload = await request.body()
    
    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Idempotency check: see if we already processed this event
    stripe_event_id = event['id']
    existing_event = await db.execute(select(StripeEvent).where(StripeEvent.stripe_event_id == stripe_event_id))
    if existing_event.scalar_one_or_none():
        print(f"Stripe event {stripe_event_id} already processed. Skipping.")
        return {"status": "success", "message": "Already processed"}

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        workspace_id_str = session.get('client_reference_id')
        metadata = session.get('metadata', {})
        credits_str = metadata.get('credits')
        
        if workspace_id_str and credits_str:
            workspace_id = uuid.UUID(workspace_id_str)
            credits_amount = int(credits_str)
            
            # Fetch or create CreditBalance
            result = await db.execute(select(CreditBalance).where(CreditBalance.workspace_id == workspace_id))
            balance = result.scalar_one_or_none()
            
            if not balance:
                balance = CreditBalance(workspace_id=workspace_id, balance=0)
                db.add(balance)
                await db.flush()
                
            balance.balance += credits_amount
            
            # Record Transaction
            transaction = CreditTransaction(
                workspace_id=workspace_id,
                amount=credits_amount,
                transaction_type="purchase",
                stripe_payment_id=session.get('payment_intent'),
                status="completed"
            )
            db.add(transaction)
            
            # Record Stripe Event
            stripe_event_record = StripeEvent(
                stripe_event_id=stripe_event_id,
                event_type=event['type'],
                status="processed"
            )
            db.add(stripe_event_record)
            
            await db.commit()
            print(f"Added {credits_amount} credits to workspace {workspace_id}")

    return {"status": "success"}
