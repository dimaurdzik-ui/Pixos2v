import uuid
from sqlalchemy import Column, String, ForeignKey, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

class Team(Base, TimestampMixin):
    __tablename__ = "teams"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(String, nullable=True)
    team_type = Column(String(50), nullable=False, default="standard")

    # Relationships
    workspace = relationship("Workspace")
    members = relationship("TeamMember", back_populates="team", cascade="all, delete-orphan")

class Agent(Base, TimestampMixin):
    __tablename__ = "agents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id", ondelete="SET NULL"), nullable=True)
    name = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)
    job_title = Column(String(255), nullable=True)
    description = Column(String, nullable=True)
    system_prompt = Column(String, nullable=True)
    model = Column(String(50), nullable=False, default="gpt-4o")
    autonomy_level = Column(String(50), nullable=False, default="balanced") # strict, balanced, full_auto
    safety_level = Column(String(50), nullable=False, default="high")
    status = Column(String(50), nullable=False, default="active") # active, inactive, archived
    is_coordinator = Column(Boolean, nullable=False, default=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    workspace = relationship("Workspace")
    memories = relationship("AgentMemory", back_populates="agent", cascade="all, delete-orphan")
    teams = relationship("TeamMember", back_populates="agent", cascade="all, delete-orphan")

class TeamMember(Base, TimestampMixin):
    __tablename__ = "team_members"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    role_in_team = Column(String(50), nullable=False, default="member")

    # Relationships
    team = relationship("Team", back_populates="members")
    agent = relationship("Agent", back_populates="teams")

class AgentMemory(Base, TimestampMixin):
    __tablename__ = "agent_memories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    key = Column(String(255), nullable=False)
    value = Column(JSON, nullable=False)

    # Relationships
    agent = relationship("Agent", back_populates="memories")
