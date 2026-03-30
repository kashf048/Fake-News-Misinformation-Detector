"""
Unit tests for authentication module
"""

import pytest
from app.security.auth import (
    PasswordHasher,
    JWTHandler,
    TokenData,
)


class TestPasswordHasher:
    """Test password hashing"""

    def test_hash_password(self):
        """Test password hashing"""
        password = "TestPassword123!"
        hashed = PasswordHasher.hash_password(password)

        assert hashed != password
        assert len(hashed) > 0

    def test_verify_password_correct(self):
        """Test password verification with correct password"""
        password = "TestPassword123!"
        hashed = PasswordHasher.hash_password(password)

        assert PasswordHasher.verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password"""
        password = "TestPassword123!"
        wrong_password = "WrongPassword123!"
        hashed = PasswordHasher.hash_password(password)

        assert PasswordHasher.verify_password(wrong_password, hashed) is False


class TestJWTHandler:
    """Test JWT token handling"""

    def test_create_access_token(self):
        """Test access token creation"""
        user_id = "test_user_123"
        email = "test@example.com"

        token = JWTHandler.create_access_token(user_id, email)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_refresh_token(self):
        """Test refresh token creation"""
        user_id = "test_user_123"
        email = "test@example.com"

        token = JWTHandler.create_refresh_token(user_id, email)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_token_valid(self):
        """Test token verification with valid token"""
        user_id = "test_user_123"
        email = "test@example.com"

        token = JWTHandler.create_access_token(user_id, email)
        token_data = JWTHandler.verify_token(token)

        assert token_data is not None
        assert token_data.user_id == user_id
        assert token_data.email == email

    def test_verify_token_invalid(self):
        """Test token verification with invalid token"""
        invalid_token = "invalid.token.here"
        token_data = JWTHandler.verify_token(invalid_token)

        assert token_data is None

    def test_create_tokens(self):
        """Test creating both tokens"""
        user_id = "test_user_123"
        email = "test@example.com"

        response = JWTHandler.create_tokens(user_id, email)

        assert response.access_token is not None
        assert response.refresh_token is not None
        assert response.token_type == "bearer"
        assert response.expires_in > 0


if __name__ == "__main__":
    pytest.main([__file__])
