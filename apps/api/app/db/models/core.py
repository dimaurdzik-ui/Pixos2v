import uuid
from sqlalchemy import Column, String, ForeignKey, Enum, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin
import enum

class RoleEnum(str, enum.Enum):
    owner = "owner"
    admin = "admin"
    manager = "manager"
    member = "member"
    viewer = "viewer"

class User(Base, TimestampMixin):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String)
    is_super_admin = Column(Boolean, default=False, nullable=False)

class Workspace(Base, TimestampMixin):
    __tablename__ = "workspaces"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

class WorkspaceMember(Base, TimestampMixin):
    __tablename__ = "workspace_members"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role = Column(Enum(RoleEnum), nullable=False)

class AuditLog(Base, TimestampMixin):
    __tablename__ = "audit_logs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    actor_type = Column(String, nullable=False) # e.g., 'user', 'system'
    actor_id = Column(UUID(as_uuid=True), nullable=True)
    action = Column(String, nullable=False)
    resource_type = Column(String, nullable=False)
    resource_id = Column(String, nullable=True)
    metadata_ = Column("metadata", JSON, nullable=True) # renamed to avoid conflict with Base.metadata
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
