from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from typing import Optional

from apps.api.app.db.models.core import Workspace, WorkspaceMember, RoleEnum

async def create_workspace_for_user(db: AsyncSession, user_id: UUID, workspace_name: str) -> Workspace:
    # 1. Create Workspace
    workspace = Workspace(name=workspace_name)
    db.add(workspace)
    await db.flush() # To get the workspace.id

    # 2. Add User as Owner
    member = WorkspaceMember(
        workspace_id=workspace.id,
        user_id=user_id,
        role=RoleEnum.owner
    )
    db.add(member)
    
    # Also seed default Coordinator agent and starter team here later
    # ...
    
    await db.commit()
    return workspace

async def check_user_access(db: AsyncSession, user_id: UUID, workspace_id: UUID) -> Optional[WorkspaceMember]:
    result = await db.execute(
        select(WorkspaceMember).where(
            WorkspaceMember.user_id == user_id,
            WorkspaceMember.workspace_id == workspace_id
        )
    )
    return result.scalar_one_or_none()
