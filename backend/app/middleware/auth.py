"""Authentication and authorization middleware."""
import uuid
from typing import Optional
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings
from app.database import get_db
from app.models.org import OrgMembership


security = HTTPBearer()


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware to validate Supabase JWT and attach user info to request."""
    
    async def dispatch(self, request: Request, call_next):
        """Process each request."""
        # Skip auth for health check and docs
        if request.url.path in ["/health", "/docs", "/openapi.json", "/redoc"]:
            return await call_next(request)
        
        # Extract token
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            # Allow request to proceed, let route handlers enforce auth
            return await call_next(request)
        
        token = auth_header.split(" ")[1]
        
        try:
            # Decode JWT
            payload = jwt.decode(
                token,
                settings.supabase_jwt_secret,
                algorithms=["HS256"],
                audience="authenticated",
            )
            
            # Attach user info to request state
            request.state.user_id = payload.get("sub")
            request.state.user_email = payload.get("email")
            request.state.user_role = payload.get("role")
            
        except JWTError:
            # Invalid token - let route handlers decide if auth is required
            pass
        
        return await call_next(request)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """Dependency to get current authenticated user."""
    token = credentials.credentials
    
    try:
        payload = jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            audience="authenticated",
        )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
        
        return {
            "id": user_id,
            "email": payload.get("email"),
            "role": payload.get("role"),
        }
    
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        ) from e


async def require_org_access(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    required_role: Optional[str] = None,  # owner, admin, member, viewer
) -> tuple[uuid.UUID, dict]:
    """
    Dependency to require org access.
    Returns (org_id, user).
    
    Args:
        request: FastAPI request
        db: Database session
        current_user: Current authenticated user
        required_role: Minimum required role (owner > admin > member > viewer)
    
    Raises:
        HTTPException: If org_id header missing or user not authorized
    """
    # Get org_id from header
    org_id_str = request.headers.get("X-Org-Id")
    if not org_id_str:
        # Try query param as fallback
        org_id_str = request.query_params.get("org_id")
    
    if not org_id_str:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-Org-Id header required",
        )
    
    try:
        org_id = uuid.UUID(org_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid org_id format",
        )
    
    # Check user membership
    user_id = uuid.UUID(current_user["id"])
    
    result = await db.execute(
        select(OrgMembership)
        .where(OrgMembership.org_id == org_id)
        .where(OrgMembership.user_id == user_id)
    )
    membership = result.scalar_one_or_none()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: not a member of this organization",
        )
    
    # Check role if required
    if required_role:
        role_hierarchy = {
            "viewer": 0,
            "member": 1,
            "admin": 2,
            "owner": 3,
        }
        
        user_role_level = role_hierarchy.get(membership.role, 0)
        required_role_level = role_hierarchy.get(required_role, 0)
        
        if user_role_level < required_role_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: {required_role} role required",
            )
    
    # Attach to request state for convenience
    request.state.org_id = org_id
    request.state.org_role = membership.role
    
    return org_id, current_user


async def get_user_org(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> tuple[uuid.UUID, dict]:
    """
    Get user's organization automatically (uses first org if user has multiple).
    Returns (org_id, user).
    """
    user_id = uuid.UUID(current_user["id"])
    
    # Get user's first org membership
    result = await db.execute(
        select(OrgMembership)
        .where(OrgMembership.user_id == user_id)
        .limit(1)
    )
    membership = result.scalar_one_or_none()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No organization found. Please contact support.",
        )
    
    return membership.org_id, current_user


def require_role(role: str):
    """
    Decorator to require specific org role.
    
    Usage:
        @router.get("/admin")
        async def admin_endpoint(
            auth: tuple = Depends(require_role("admin"))
        ):
            org_id, user = auth
            ...
    """
    async def dependency(
        request: Request,
        db: AsyncSession = Depends(get_db),
        current_user: dict = Depends(get_current_user),
    ):
        return await require_org_access(request, db, current_user, required_role=role)
    
    return dependency

