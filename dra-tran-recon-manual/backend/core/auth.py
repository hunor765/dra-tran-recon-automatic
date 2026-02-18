"""Authentication and authorization utilities.

Provides JWT token validation via Supabase Auth and role-based access control.
"""
import logging
from typing import Optional, Dict, Any

import httpx
import jwt
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.config import settings
from core.database import get_db
from models.client import Client
from models.user_client import UserClient

logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)

# Supabase configuration
SUPABASE_URL = settings.SUPABASE_URL or ""
SUPABASE_ANON_KEY = settings.SUPABASE_ANON_KEY or ""
SUPABASE_JWT_SECRET = settings.SUPABASE_JWT_SECRET or ""

# Admin email patterns for role determination
ADMIN_EMAIL_PATTERNS = [
    "@dra.com",
    "@datarevolt.ro",
    "@revolt.agency",
]


class AuthError(Exception):
    """Authentication/authorization error."""
    pass


class TokenValidationError(AuthError):
    """JWT token validation error."""
    pass


def _is_admin_email(email: str) -> bool:
    """Check if email matches admin patterns.
    
    Args:
        email: User email address
        
    Returns:
        bool: True if email matches admin patterns
    """
    email_lower = email.lower()
    return any(pattern in email_lower for pattern in ADMIN_EMAIL_PATTERNS)


async def _validate_token_with_supabase(token: str) -> Dict[str, Any]:
    """Validate JWT token with Supabase Auth API.
    
    Args:
        token: JWT access token from Supabase
        
    Returns:
        dict: User data from Supabase
        
    Raises:
        TokenValidationError: If token is invalid or expired
    """
    # First, try to validate locally with JWT secret (faster)
    if SUPABASE_JWT_SECRET:
        try:
            payload = jwt.decode(
                token,
                SUPABASE_JWT_SECRET,
                algorithms=["HS256"],
                audience="authenticated",
            )
            return {
                "id": payload.get("sub"),
                "email": payload.get("email"),
                "role": payload.get("role", "authenticated"),
                "app_metadata": payload.get("app_metadata", {}),
                "user_metadata": payload.get("user_metadata", {}),
            }
        except jwt.ExpiredSignatureError:
            raise TokenValidationError("Token has expired")
        except jwt.InvalidTokenError as e:
            logger.debug(f"Local JWT validation failed, falling back to API: {e}")
            # Fall through to API validation
    
    # Fallback: Validate with Supabase Auth API
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        raise TokenValidationError(
            "Supabase configuration missing. Set SUPABASE_URL and SUPABASE_ANON_KEY."
        )
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{SUPABASE_URL}/auth/v1/user",
                headers={
                    "Authorization": f"Bearer {token}",
                    "apikey": SUPABASE_ANON_KEY,
                },
                timeout=10.0,
            )
            
            if response.status_code == 401:
                raise TokenValidationError("Invalid or expired token")
            elif response.status_code != 200:
                logger.error(f"Supabase auth error: {response.status_code} - {response.text}")
                raise TokenValidationError("Authentication service error")
            
            user_data = response.json()
            return {
                "id": user_data.get("id"),
                "email": user_data.get("email"),
                "role": user_data.get("role", "authenticated"),
                "app_metadata": user_data.get("app_metadata", {}),
                "user_metadata": user_data.get("user_metadata", {}),
            }
            
    except httpx.RequestError as e:
        logger.error(f"Supabase request failed: {e}")
        raise TokenValidationError("Authentication service unavailable")


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Dict[str, Any]:
    """Validate JWT token and return user info.
    
    Args:
        credentials: HTTP Authorization credentials
        
    Returns:
        dict: User information including id, email, and role
        
    Raises:
        HTTPException: If authentication fails
    """
    # Development bypass (only in development environment)
    if settings.ENVIRONMENT == "development":
        if not credentials:
            logger.debug("Development mode: allowing unauthenticated request")
            return {
                "id": "dev-user",
                "email": "dev@localhost",
                "role": "admin",  # Dev user has admin access
            }
    
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    try:
        user_data = await _validate_token_with_supabase(token)
        
        # Determine role based on email patterns
        email = user_data.get("email", "")
        if _is_admin_email(email) or user_data.get("app_metadata", {}).get("role") == "admin":
            user_data["role"] = "admin"
        else:
            user_data["role"] = user_data.get("user_metadata", {}).get("role", "client")
        
        logger.debug(
            "Authenticated user",
            extra={
                "user_id": user_data["id"],
                "email": email,
                "role": user_data["role"],
            },
        )
        
        return user_data
        
    except TokenValidationError as e:
        logger.warning(f"Token validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Unexpected auth error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication error",
        )


async def get_current_client_id(
    user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Optional[int]:
    """Get the client_id for the current user.
    
    Admin users can access all clients (returns None).
    Regular users must have a user_client mapping.
    
    Args:
        user: Current user from get_current_user
        db: Database session
        
    Returns:
        Optional[int]: Client ID for regular users, None for admins
    """
    if user.get("role") == "admin":
        return None
    
    user_id = user.get("id")
    
    try:
        result = await db.execute(
            select(UserClient.client_id)
            .where(UserClient.user_id == user_id)
            .where(UserClient.status == "active")
        )
        client_id = result.scalar_one_or_none()
        
        if client_id:
            logger.debug(f"User {user_id} mapped to client {client_id}")
        else:
            logger.warning(f"User {user_id} has no client mapping")
        
        return client_id
        
    except Exception as e:
        logger.error(f"Error fetching client mapping: {e}", exc_info=True)
        return None


def require_admin(user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Require admin role.
    
    Args:
        user: Current user from get_current_user
        
    Returns:
        dict: User data if admin
        
    Raises:
        HTTPException: If user is not an admin
    """
    if user.get("role") != "admin":
        logger.warning(
            f"Admin access denied for user {user.get('email')}",
            extra={"user_id": user.get("id"), "attempted_role": user.get("role")},
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return user


async def require_client_access(
    client_id: int,
    user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> bool:
    """Verify user has access to a specific client.
    
    Args:
        client_id: The client ID to check access for
        user: Current user from get_current_user
        db: Database session
        
    Returns:
        bool: True if access is granted
        
    Raises:
        HTTPException: If user doesn't have access to the client
    """
    # Admins can access all clients
    if user.get("role") == "admin":
        return True
    
    user_id = user.get("id")
    
    try:
        result = await db.execute(
            select(UserClient)
            .where(UserClient.user_id == user_id)
            .where(UserClient.client_id == client_id)
            .where(UserClient.status == "active")
        )
        
        if result.scalar_one_or_none():
            logger.debug(f"User {user_id} granted access to client {client_id}")
            return True
        
        logger.warning(
            f"Access denied: user {user_id} attempted access to client {client_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied for this client",
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking client access: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error verifying access",
        )
