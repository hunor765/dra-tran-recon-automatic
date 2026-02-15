from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class ConnectorBase(BaseModel):
    type: str = Field(..., description="Connector type: ga4, shopify, woocommerce")


class ConnectorCreate(ConnectorBase):
    config: Dict[str, Any] = Field(..., description="Connector configuration")


class ConnectorUpdate(BaseModel):
    type: Optional[str] = None
    config: Optional[Dict[str, Any]] = None


class Connector(ConnectorBase):
    id: int
    client_id: int
    config_json: str
    
    class Config:
        from_attributes = True
