from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, Dict, Any
import os

from core.database import get_db
from core.config import settings
from models.client import Client
from models.user_client import UserClient

security = HTTPBearer(auto_error=False)

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Dict[str, Any]:
    """Validate JWT token and return user info"""
    # For development, return mock admin user
    # In production, validate Supabase JWT
    if not credentials:
        # Allow requests without auth in development
        if settings.ENVIRONMENT == "development":
            return {"id": "dev-user", "email": "admin@dra.com", "role": "admin"}
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    # TODO: Implement proper JWT validation with Supabase
    # For now, mock the user
    return {"id": "test-user", "email": "admin@dra.com", "role": "admin"}

async def get_current_client_id(
    user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Optional[int]:
    """Get the client_id for the current user (for non-admin users)"""
    if user.get("role") == "admin":
        return None  # Admin can see all clients
    
    # For non-admin users, lookup their client assignment
    result = await db.execute(
        select(UserClient.client_id)
        .where(UserClient.user_id == user.get("id"))
        .where(UserClient.status == "active")
    )
    user_client = result.scalar_one_or_none()
    return user_client

def require_admin(user: Dict[str, Any] = Depends(get_current_user)):
    """Require admin role"""
    if user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return user

async def require_client_access(
    client_id: int,
    user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Verify user has access to a specific client"""
    if user.get("role") == "admin":
        return True
    
    result = await db.execute(
        select(UserClient)
        .where(UserClient.user_id == user.get("id"))
        .where(UserClient.client_id == client_id)
        .where(UserClient.status == "active")
    )
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied for this client"
        )
    return True
