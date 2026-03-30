"""
Authentication Module
JWT token generation, validation, and user authentication
"""

import os
from datetime import datetime, timedelta
from typing import Optional
import jwt
from passlib.context import CryptContext
from pydantic import BaseModel

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))


class TokenData(BaseModel):
    """Token payload data"""
    user_id: str
    email: str
    exp: datetime
    token_type: str


class TokenResponse(BaseModel):
    """Token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserCredentials(BaseModel):
    """User login credentials"""
    email: str
    password: str


class UserRegistration(BaseModel):
    """User registration data"""
    email: str
    password: str
    full_name: str


class PasswordHasher:
    """Password hashing utilities"""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against hash"""
        return pwd_context.verify(plain_password, hashed_password)


class JWTHandler:
    """JWT token handling"""

    @staticmethod
    def create_access_token(user_id: str, email: str) -> str:
        """Create access token"""
        expires = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {
            "user_id": user_id,
            "email": email,
            "exp": expires,
            "token_type": "access"
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def create_refresh_token(user_id: str, email: str) -> str:
        """Create refresh token"""
        expires = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        payload = {
            "user_id": user_id,
            "email": email,
            "exp": expires,
            "token_type": "refresh"
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def verify_token(token: str) -> Optional[TokenData]:
        """Verify and decode token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("user_id")
            email = payload.get("email")
            token_type = payload.get("token_type")

            if not user_id or not email:
                return None

            return TokenData(
                user_id=user_id,
                email=email,
                exp=datetime.fromtimestamp(payload.get("exp")),
                token_type=token_type
            )
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    @staticmethod
    def create_tokens(user_id: str, email: str) -> TokenResponse:
        """Create both access and refresh tokens"""
        access_token = JWTHandler.create_access_token(user_id, email)
        refresh_token = JWTHandler.create_refresh_token(user_id, email)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
