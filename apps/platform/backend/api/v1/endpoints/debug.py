"""Debug endpoints for troubleshooting authentication and connectivity issues."""
import logging
from typing import Any, Dict

from fastapi import APIRouter, Depends, Request, Header
from pydantic import BaseModel

from core.auth import get_current_user, TokenValidationError, _validate_token_with_supabase
from core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


class TokenDebugRequest(BaseModel):
    token: str


class TokenDebugResponse(BaseModel):
    valid: bool
    error: str | None = None
    user_id: str | None = None
    email: str | None = None
    role: str | None = None
    token_preview: str | None = None
    token_header: Dict[str, Any] | None = None


@router.post("/debug/validate-token", response_model=TokenDebugResponse)
async def debug_validate_token(request: TokenDebugRequest):
    """Debug endpoint to validate a token and see detailed error information.
    
    This endpoint can be used to troubleshoot why tokens are being rejected.
    """
    token = request.token
    token_preview = token[:30] + "..." if len(token) > 30 else token
    
    # Decode token header
    token_header = None
    try:
        import base64
        import json
        header_b64 = token.split('.')[0]
        padding = 4 - len(header_b64) % 4
        if padding != 4:
            header_b64 += '=' * padding
        header_json = base64.urlsafe_b64decode(header_b64)
        token_header = json.loads(header_json)
    except Exception as e:
        return TokenDebugResponse(
            valid=False,
            error=f"Invalid token format: {e}",
            token_preview=token_preview
        )
    
    # Try to validate
    try:
        user_data = await _validate_token_with_supabase(token)
        return TokenDebugResponse(
            valid=True,
            user_id=user_data.get("id"),
            email=user_data.get("email"),
            role=user_data.get("role"),
            token_preview=token_preview,
            token_header=token_header
        )
    except TokenValidationError as e:
        return TokenDebugResponse(
            valid=False,
            error=str(e),
            token_preview=token_preview,
            token_header=token_header
        )
    except Exception as e:
        return TokenDebugResponse(
            valid=False,
            error=f"Unexpected error: {e}",
            token_preview=token_preview,
            token_header=token_header
        )


@router.get("/debug/auth-check")
async def debug_auth_check(
    request: Request,
    authorization: str | None = Header(None),
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Check if authentication is working properly.
    
    Returns user info if authenticated, or detailed error if not.
    """
    return {
        "authenticated": True,
        "user_id": user.get("id"),
        "email": user.get("email"),
        "role": user.get("role"),
        "auth_header_received": authorization is not None,
        "auth_header_prefix": authorization[:50] + "..." if authorization and len(authorization) > 50 else authorization,
    }


@router.get("/debug/config-check")
async def debug_config_check():
    """Check backend configuration (no auth required).
    
    Returns configuration status without exposing sensitive values.
    """
    return {
        "environment": settings.ENVIRONMENT,
        "supabase_configured": {
            "url": bool(settings.SUPABASE_URL),
            "url_preview": settings.SUPABASE_URL[:30] + "..." if settings.SUPABASE_URL else None,
            "anon_key": bool(settings.SUPABASE_ANON_KEY),
            "jwt_secret": bool(settings.SUPABASE_JWT_SECRET),
            "jwt_secret_length": len(settings.SUPABASE_JWT_SECRET) if settings.SUPABASE_JWT_SECRET else 0,
        },
        "cors_origins": settings.CORS_ORIGINS,
        "database_configured": bool(settings.DATABASE_URL),
    }
