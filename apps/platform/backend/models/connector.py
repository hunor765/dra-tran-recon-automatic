from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from core.database import Base

class Connector(Base):
    __tablename__ = "connectors"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"))
    type = Column(String, index=True) # ga4, woocommerce, shopify
    config_json = Column(String) # Encrypted credentials

    client = relationship("Client", back_populates="connectors")
