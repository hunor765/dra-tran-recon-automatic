import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from pydantic import BaseModel, EmailStr

from core.database import get_db
from core.auth import require_admin
from core.email_service import email_service
from models.user_client import UserClient
from models.client import Client

router = APIRouter()
logger = logging.getLogger(__name__)

class UserInvite(BaseModel):
    email: EmailStr
    role: str = "viewer"  # 'admin' or 'viewer'

class UserResponse(BaseModel):
    id: int
    email: str
    role: str
    status: str
    client_id: int
    created_at: str

@router.post("/clients/{client_id}/invite")
async def invite_user(
    client_id: int,
    invite: UserInvite,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(require_admin)
):
    """Invite a user to access a client"""
    # Verify client exists
    result = await db.execute(select(Client).where(Client.id == client_id))
    client = result.scalars().first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Check if email already invited for this client
    result = await db.execute(
        select(UserClient)
        .where(UserClient.client_id == client_id)
        .where(UserClient.email == invite.email)
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="User already invited for this client")
    
    # Create user_client record
    user_client = UserClient(
        client_id=client_id,
        email=invite.email,
        role=invite.role,
        status="invited"
    )
    db.add(user_client)
    await db.commit()
    await db.refresh(user_client)
    
    # Send invitation email
    try:
        # Get the frontend URL from settings or use default
        from core.config import settings
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        invite_link = f"{frontend_url}/login?invite={user_client.id}"
        
        admin_name = admin.get('email', 'An administrator')
        
        await email_service.send_user_invitation(
            email=invite.email,
            inviter_name=admin_name,
            client_name=client.name,
            role=invite.role,
            invite_link=invite_link
        )
        
        logger.info(
            f"Invitation email sent to {invite.email} for client {client.name}",
            extra={
                "email": invite.email,
                "client_id": client_id,
                "inviter": admin.get('id'),
                "role": invite.role
            }
        )
        
    except Exception as e:
        # Log the error but don't fail the invitation
        # The user can still be invited and the admin can resend if needed
        logger.error(
            f"Failed to send invitation email to {invite.email}: {e}",
            extra={
                "email": invite.email,
                "client_id": client_id,
                "error": str(e)
            },
            exc_info=True
        )
    
    return {
        "message": "Invitation sent successfully",
        "user": {
            "id": user_client.id,
            "email": user_client.email,
            "role": user_client.role,
            "status": user_client.status
        }
    }

@router.get("/clients/{client_id}/users", response_model=List[UserResponse])
async def list_client_users(
    client_id: int,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(require_admin)
):
    """List all users for a client"""
    result = await db.execute(
        select(UserClient)
        .where(UserClient.client_id == client_id)
        .order_by(UserClient.created_at.desc())
    )
    users = result.scalars().all()
    
    return [
        {
            "id": u.id,
            "email": u.email,
            "role": u.role,
            "status": u.status,
            "client_id": u.client_id,
            "created_at": u.created_at.isoformat() if u.created_at else None
        }
        for u in users
    ]

@router.delete("/users/{user_client_id}")
async def remove_user(
    user_client_id: int,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(require_admin)
):
    """Remove a user's access to a client"""
    result = await db.execute(
        select(UserClient).where(UserClient.id == user_client_id)
    )
    user_client = result.scalar_one_or_none()
    if not user_client:
        raise HTTPException(status_code=404, detail="User not found")
    
    await db.delete(user_client)
    await db.commit()
    
    return {"message": "User access revoked successfully"}
