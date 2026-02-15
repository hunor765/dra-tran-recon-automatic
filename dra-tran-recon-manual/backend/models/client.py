from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base

class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    slug = Column(String, unique=True, index=True)
    logo_url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    jobs = relationship("Job", back_populates="client")
    connectors = relationship("Connector", back_populates="client")
    schedule = relationship("Schedule", back_populates="client", uselist=False)
