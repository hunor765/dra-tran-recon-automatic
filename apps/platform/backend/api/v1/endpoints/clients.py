from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from core.database import get_db
from core.auth import get_current_user, require_admin
from models.client import Client as ClientModel
from schemas.client import Client, ClientCreate
from sqlalchemy import select

router = APIRouter()

@router.post("/", response_model=Client)
async def create_client(client: ClientCreate, db: AsyncSession = Depends(get_db)):
    db_client = ClientModel(name=client.name, slug=client.slug, logo_url=client.logo_url)
    db.add(db_client)
    await db.commit()
    await db.refresh(db_client)
    return db_client

@router.get("/", response_model=List[Client])
async def read_clients(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ClientModel).offset(skip).limit(limit))
    clients = result.scalars().all()
    return clients

@router.get("/{client_id}", response_model=Client)
async def get_client(
    client_id: int,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """Get a specific client by ID"""
    result = await db.execute(select(ClientModel).where(ClientModel.id == client_id))
    client = result.scalars().first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client

@router.put("/{client_id}", response_model=Client)
async def update_client(
    client_id: int,
    client_update: ClientCreate,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_admin)
):
    """Update a client"""
    result = await db.execute(select(ClientModel).where(ClientModel.id == client_id))
    client = result.scalars().first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    client.name = client_update.name
    client.slug = client_update.slug
    if client_update.logo_url:
        client.logo_url = client_update.logo_url
    
    await db.commit()
    await db.refresh(client)
    return client

@router.delete("/{client_id}")
async def delete_client(
    client_id: int,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_admin)
):
    """Delete a client"""
    result = await db.execute(select(ClientModel).where(ClientModel.id == client_id))
    client = result.scalars().first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    await db.delete(client)
    await db.commit()
    return {"message": "Client deleted successfully"}
