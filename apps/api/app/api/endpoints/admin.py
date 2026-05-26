from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from pydantic import BaseModel

from apps.api.app.db.database import get_db
from apps.api.app.db.models.core import User
from apps.api.app.db.models.system import SystemConfig
from apps.api.app.api.deps import require_super_admin
from apps.api.app.core.encryption import encrypt_value

router = APIRouter()

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
    
    encrypted = encrypt_value(config.value)
    
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
        
    await db.commit()
    return {"status": "success"}
