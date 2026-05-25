import uuid
from sqlalchemy import Column, String, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

class Team(Base, TimestampMixin):
    __tablename__ = "teams"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    description = Column(String, nullable=True)

    # Relationships
    workspace = relationship("Workspace")
    members = relationship("TeamMember", back_populates="team", cascade="all, delete-orphan")

class Agent(Base, TimestampMixin):
    __tablename__ = "agents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(50), nullable=False, default="active")

    # Relationships
    workspace = relationship("Workspace")
    profile = relationship("AgentProfile", back_populates="agent", uselist=False, cascade="all, delete-orphan")
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

class AgentProfile(Base, TimestampMixin):
    __tablename__ = "agent_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, unique=True)
    system_prompt = Column(String, nullable=True)
    autonomy_level = Column(String(50), nullable=False, default="medium")
    settings = Column(JSON, nullable=True)

    # Relationships
    agent = relationship("Agent", back_populates="profile")

class AgentMemory(Base, TimestampMixin):
    __tablename__ = "agent_memories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    key = Column(String(255), nullable=False)
    value = Column(JSON, nullable=False)

    # Relationships
    agent = relationship("Agent", back_populates="memories")
