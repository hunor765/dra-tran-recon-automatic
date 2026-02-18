from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ClientBase(BaseModel):
    name: str
    slug: str
    logo_url: Optional[str] = None

class ClientCreate(ClientBase):
    pass

class Client(ClientBase):
    id: int
    is_active: bool = True
    created_at: datetime

    class Config:
        from_attributes = True
