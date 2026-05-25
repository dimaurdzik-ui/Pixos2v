import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from apps.api.app.db.models.core import Workspace, WorkspaceMember, AuditLog, RoleEnum
from apps.api.app.db.models.agents import Agent, Team, TeamMember
from apps.api.app.db.models.policy import ToolPolicy
from apps.api.app.db.models.billing import CreditBalance

async def initialize_workspace_resources(db: AsyncSession, workspace_id: uuid.UUID, owner_id: uuid.UUID):
    """
    Initializes a new workspace with default starter kit:
    - WorkspaceMember (owner)
    - Coordinator Agent
    - Starter Team
    - Default ToolPolicies
    - CreditBalance
    - AuditLog
    """
    
    # 1. Add Owner to WorkspaceMember
    owner_member = WorkspaceMember(
        workspace_id=workspace_id,
        user_id=owner_id,
        role=RoleEnum.owner
    )
    db.add(owner_member)
    
    # 2. Coordinator Agent
    coordinator_agent = Agent(
        id=uuid.UUID("11111111-1111-1111-1111-111111111111"), # fixed id for now, could be dynamic
        name="System Coordinator",
        role="coordinator",
        workspace_id=workspace_id,
        status="active"
    )
    db.add(coordinator_agent)
    
    # 3. Starter Team
    starter_team = Team(
        name="Main Team",
        workspace_id=workspace_id,
        description="Default team for AI Agents"
    )
    db.add(starter_team)
    
    # Flush to get starter_team id if we needed it (not strictly necessary here as we just added it)
    await db.flush()
    
    # Add Coordinator to Team (optional but good practice)
    team_member = TeamMember(
        team_id=starter_team.id,
        agent_id=coordinator_agent.id,
        role_in_team="admin"
    )
    db.add(team_member)
    
    # 4. Tool Policies
    # web.search -> auto
    policy_search = ToolPolicy(
        workspace_id=workspace_id,
        tool_name="web.search",
        risk_level="LOW",
        approval_required="auto"
    )
    # gmail.send -> approval_required
    policy_gmail = ToolPolicy(
        workspace_id=workspace_id,
        tool_name="gmail.send",
        risk_level="HIGH",
        approval_required="approval_required"
    )
    db.add_all([policy_search, policy_gmail])
    
    # 5. Credit Balance
    balance = CreditBalance(
        workspace_id=workspace_id,
        balance=100
    )
    db.add(balance)
    
    # 6. Audit Log
    log = AuditLog(
        workspace_id=workspace_id,
        actor_type="system",
        actor_id=owner_id,
        action="workspace.initialized",
        resource_type="workspace",
        resource_id=str(workspace_id),
        metadata_={"info": "Seeded starter resources"}
    )
    db.add(log)
    
    await db.commit()
