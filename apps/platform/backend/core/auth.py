"""Authentication and authorization utilities.

Provides JWT token validation via Supabase Auth and role-based access control.
"""
import logging
import base64
import json
from datetime import datetime
from typing import Optional, Dict, Any, Tuple

import httpx
import jwt
from jwt.algorithms import ECAlgorithm
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
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

# JWKS cache
_jwks_cache: Optional[Dict[str, Any]] = None
_jwks_last_fetch: Optional[datetime] = None

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


def _decode_token_parts(token: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Decode token header and payload without verification.
    
    Args:
        token: JWT token string
        
    Returns:
        Tuple of (header_dict, payload_dict)
    """
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return {}, {}
        
        # Decode header
        header_b64 = parts[0]
        padding = 4 - len(header_b64) % 4
        if padding != 4:
            header_b64 += '=' * padding
        header_json = base64.urlsafe_b64decode(header_b64)
        header = json.loads(header_json)
        
        # Decode payload
        payload_b64 = parts[1]
        padding = 4 - len(payload_b64) % 4
        if padding != 4:
            payload_b64 += '=' * padding
        payload_json = base64.urlsafe_b64decode(payload_b64)
        payload = json.loads(payload_json)
        
        return header, payload
    except Exception as e:
        logger.warning(f"Could not decode token parts: {e}")
        return {}, {}


async def _fetch_jwks() -> Optional[Dict[str, Any]]:
    """Fetch JWKS (JSON Web Key Set) from Supabase.
    
    Returns:
        dict: JWKS containing public keys, or None if fetch fails
    """
    global _jwks_cache, _jwks_last_fetch
    
    # Use cache if available (JWKS rarely changes)
    if _jwks_cache and _jwks_last_fetch:
        from datetime import timedelta
        if datetime.utcnow() - _jwks_last_fetch < timedelta(hours=1):
            return _jwks_cache
    
    if not SUPABASE_URL:
        return None
    
    try:
        clean_url = SUPABASE_URL.rstrip('/')
        jwks_url = f"{clean_url}/.well-known/jwks.json"
        
        logger.debug(f"Fetching JWKS from: {jwks_url}")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(jwks_url, timeout=10.0)
            
            if response.status_code == 200:
                _jwks_cache = response.json()
                _jwks_last_fetch = datetime.utcnow()
                logger.debug("JWKS fetched and cached successfully")
                return _jwks_cache
            else:
                logger.warning(f"Failed to fetch JWKS: {response.status_code}")
                return None
                
    except Exception as e:
        logger.warning(f"Error fetching JWKS: {e}")
        return None


def _get_public_key_from_jwks(jwks: Dict[str, Any], kid: str) -> Optional[str]:
    """Extract public key in PEM format from JWKS for given key ID.
    
    Args:
        jwks: JWKS dictionary
        kid: Key ID from token header
        
    Returns:
        str: Public key in PEM format, or None if not found
    """
    try:
        keys = jwks.get('keys', [])
        for key in keys:
            if key.get('kid') == kid:
                # Convert JWK to PEM
                if key.get('kty') == 'EC' and key.get('crv') == 'P-256':
                    # ES256 key
                    x = base64.urlsafe_b64decode(key['x'] + '===')
                    y = base64.urlsafe_b64decode(key['y'] + '===')
                    
                    # Build uncompressed point (0x04 || x || y)
                    point = b'\x04' + x + y
                    
                    from cryptography.hazmat.primitives.asymmetric import ec
                    public_key = ec.EllipticCurvePublicKey.from_encoded_point(
                        ec.SECP256R1(), point
                    )
                    
                    pem = public_key.public_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PublicFormat.SubjectPublicKeyInfo
                    )
                    return pem.decode('utf-8')
                    
                elif key.get('kty') == 'RSA':
                    # RSA key (for RS256)
                    from cryptography.hazmat.primitives.asymmetric import rsa
                    
                    n = int.from_bytes(
                        base64.urlsafe_b64decode(key['n'] + '==='), 'big'
                    )
                    e = int.from_bytes(
                        base64.urlsafe_b64decode(key['e'] + '==='), 'big'
                    )
                    
                    public_key = rsa.RSAPublicNumbers(e, n).public_key(default_backend())
                    pem = public_key.public_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PublicFormat.SubjectPublicKeyInfo
                    )
                    return pem.decode('utf-8')
        
        logger.warning(f"Key with kid '{kid}' not found in JWKS")
        return None
        
    except Exception as e:
        logger.error(f"Error extracting public key from JWKS: {e}")
        return None


async def _validate_token_with_supabase(token: str) -> Dict[str, Any]:
    """Validate JWT token with Supabase Auth.
    
    For ES256/RS256 tokens: Uses JWKS to get public key for local validation
    For HS256 tokens: Uses JWT secret for local validation
    Falls back to Supabase Auth API if local validation fails.
    
    Args:
        token: JWT access token from Supabase
        
    Returns:
        dict: User data from Supabase
        
    Raises:
        TokenValidationError: If token is invalid or expired
    """
    import time
    
    logger.info(f"Validating token. JWT_SECRET configured: {bool(SUPABASE_JWT_SECRET)}, SUPABASE_URL configured: {bool(SUPABASE_URL)}")
    
    # Decode token header and payload without verification
    token_header, token_payload = _decode_token_parts(token)
    token_alg = token_header.get('alg', 'unknown')
    token_kid = token_header.get('kid')
    
    token_preview = token[:30] + "..." if len(token) > 30 else token
    logger.info(f"Token preview: {token_preview}")
    logger.info(f"Token algorithm: {token_alg}, Key ID: {token_kid}")
    
    # Check expiration
    exp = token_payload.get('exp')
    if exp:
        now = time.time()
        if now > exp:
            logger.warning(f"Token expired by {now - exp} seconds")
            raise TokenValidationError("Token has expired")
        else:
            logger.info(f"Token valid for {exp - now} more seconds")
    
    # Try local validation first (faster than API call)
    
    # For asymmetric algorithms (ES256, RS256), fetch public key from JWKS
    if token_alg in ['ES256', 'RS256']:
        try:
            jwks = await _fetch_jwks()
            if jwks and token_kid:
                public_key_pem = _get_public_key_from_jwks(jwks, token_kid)
                if public_key_pem:
                    payload = jwt.decode(
                        token,
                        public_key_pem,
                        algorithms=[token_alg],
                        audience="authenticated",
                    )
                    logger.info(f"Token validated locally using JWKS public key ({token_alg})")
                    return {
                        "id": payload.get("sub"),
                        "email": payload.get("email"),
                        "role": payload.get("role", "authenticated"),
                        "app_metadata": payload.get("app_metadata", {}),
                        "user_metadata": payload.get("user_metadata", {}),
                    }
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired (JWKS validation)")
            raise TokenValidationError("Token has expired")
        except Exception as e:
            logger.debug(f"JWKS local validation failed: {e}")
            # Fall through to API validation
    
    # For symmetric algorithm (HS256), try JWT secret
    elif token_alg == 'HS256' and SUPABASE_JWT_SECRET:
        try:
            payload = jwt.decode(
                token,
                SUPABASE_JWT_SECRET,
                algorithms=["HS256"],
                audience="authenticated",
            )
            logger.info("Token validated locally using JWT secret (HS256)")
            return {
                "id": payload.get("sub"),
                "email": payload.get("email"),
                "role": payload.get("role", "authenticated"),
                "app_metadata": payload.get("app_metadata", {}),
                "user_metadata": payload.get("user_metadata", {}),
            }
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired (HS256 validation)")
            raise TokenValidationError("Token has expired")
        except Exception as e:
            logger.debug(f"HS256 local validation failed: {e}")
            # Fall through to API validation
    
    # Fallback: Use Supabase Auth API for validation
    logger.info(f"Falling back to Supabase Auth API for validation")
    
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        logger.error(f"Missing Supabase config: URL={bool(SUPABASE_URL)}, ANON_KEY={bool(SUPABASE_ANON_KEY)}")
        raise TokenValidationError(
            "Supabase configuration missing. Set SUPABASE_URL and SUPABASE_ANON_KEY."
        )
    
    try:
        clean_url = SUPABASE_URL.rstrip('/')
        api_endpoint = f"{clean_url}/auth/v1/user"
        
        logger.info(f"Calling Supabase Auth API: {clean_url[:30]}.../auth/v1/user")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                api_endpoint,
                headers={
                    "Authorization": f"Bearer {token}",
                    "apikey": SUPABASE_ANON_KEY,
                },
                timeout=10.0,
            )
            
            logger.info(f"Supabase API response status: {response.status_code}")
            
            if response.status_code == 401:
                logger.warning(f"Supabase API returned 401 - token is invalid or expired")
                raise TokenValidationError("Invalid or expired token")
            elif response.status_code == 404:
                logger.error(f"Supabase API endpoint not found: {api_endpoint}")
                raise TokenValidationError("Auth endpoint not found - check SUPABASE_URL")
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
        logger.warning("No credentials provided in Authorization header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required - no Bearer token in Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    # Log token prefix for debugging (don't log full token for security)
    token_preview = token[:20] + "..." if len(token) > 20 else "invalid"
    logger.info(f"Received token: {token_preview} (scheme: {credentials.scheme})")
    
    if not token or token == "null" or token == "undefined":
        logger.warning(f"Empty or invalid token value: '{token}'")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        user_data = await _validate_token_with_supabase(token)
        logger.info(f"Token validated successfully for user: {user_data.get('email')}")
        
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
