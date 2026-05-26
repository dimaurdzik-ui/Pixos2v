from fastapi import APIRouter, Depends
from apps.api.app.db.models.core import User
from apps.api.app.api.deps import get_current_user
from pydantic import BaseModel

router = APIRouter()

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    is_super_admin: bool

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        full_name=current_user.full_name,
        is_super_admin=current_user.is_super_admin
    )
