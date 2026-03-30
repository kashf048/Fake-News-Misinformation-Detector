"""Security module"""

from app.security.auth import (
    JWTHandler,
    PasswordHasher,
    TokenData,
    TokenResponse,
    UserCredentials,
    UserRegistration,
)
from app.security.dependencies import (
    get_current_user,
    get_optional_user,
    verify_user_exists,
    verify_admin_role,
)

__all__ = [
    "JWTHandler",
    "PasswordHasher",
    "TokenData",
    "TokenResponse",
    "UserCredentials",
    "UserRegistration",
    "get_current_user",
    "get_optional_user",
    "verify_user_exists",
    "verify_admin_role",
]
