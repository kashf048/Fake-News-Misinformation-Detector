"""
Security Dependencies
FastAPI dependencies for authentication and authorization
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from app.security.auth import JWTHandler, TokenData
from app.services.user import UserService

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthCredentials = Depends(security),
) -> TokenData:
    """
    Get current authenticated user from JWT token
    """
    token = credentials.credentials

    token_data = JWTHandler.verify_token(token)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify token type
    if token_data.token_type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    return token_data


async def get_optional_user(
    credentials: Optional[HTTPAuthCredentials] = Depends(security),
) -> Optional[TokenData]:
    """
    Get optional authenticated user (can be None)
    """
    if not credentials:
        return None

    token = credentials.credentials
    token_data = JWTHandler.verify_token(token)

    if not token_data or token_data.token_type != "access":
        return None

    return token_data


async def verify_user_exists(
    token_data: TokenData = Depends(get_current_user),
) -> dict:
    """
    Verify that user exists in database
    """
    user = await UserService.get_user_by_id(token_data.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


async def verify_admin_role(
    token_data: TokenData = Depends(get_current_user),
) -> dict:
    """
    Verify that user has admin role
    """
    user = await UserService.get_user_by_id(token_data.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    return user
