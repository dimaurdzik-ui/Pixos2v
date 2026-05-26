import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from apps.api.app.db.models.base import Base, TimestampMixin

class SystemConfig(Base, TimestampMixin):
    __tablename__ = "system_configs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key_name = Column(String, unique=True, index=True, nullable=False)
    encrypted_value = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
