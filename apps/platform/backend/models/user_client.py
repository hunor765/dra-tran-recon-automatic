from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from core.database import Base

class UserClient(Base):
    __tablename__ = "user_clients"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=True)  # NULL until user accepts invite
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"))
    email = Column(String, index=True, nullable=False)  # For pre-invite
    role = Column(String, default="viewer")  # 'admin', 'viewer'
    status = Column(String, default="invited")  # 'invited', 'active', 'inactive'
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
