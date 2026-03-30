"""
User Service
User management and database operations
"""

import logging
from datetime import datetime
from typing import Optional, Dict, Any
from bson import ObjectId
from app.database import get_db
from app.security.auth import PasswordHasher

logger = logging.getLogger(__name__)


class UserService:
    """User management service"""

    @staticmethod
    async def create_user(email: str, password: str, full_name: str) -> Dict[str, Any]:
        """Create a new user"""
        db = await get_db()

        # Check if user already exists
        existing_user = await db.users.find_one({"email": email})
        if existing_user:
            raise ValueError("User with this email already exists")

        # Hash password
        hashed_password = PasswordHasher.hash_password(password)

        # Create user document
        user_doc = {
            "email": email,
            "password": hashed_password,
            "full_name": full_name,
            "role": "user",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "last_login": None,
            "preferences": {
                "notifications_enabled": True,
                "email_notifications": True,
            }
        }

        result = await db.users.insert_one(user_doc)
        user_doc["_id"] = result.inserted_id

        logger.info(f"User created: {email}")
        return UserService._format_user(user_doc)

    @staticmethod
    async def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        db = await get_db()
        user = await db.users.find_one({"email": email})
        return UserService._format_user(user) if user else None

    @staticmethod
    async def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        db = await get_db()
        try:
            user = await db.users.find_one({"_id": ObjectId(user_id)})
            return UserService._format_user(user) if user else None
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None

    @staticmethod
    async def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with email and password"""
        user = await UserService.get_user_by_email(email)
        if not user:
            return None

        if not PasswordHasher.verify_password(password, user.get("password", "")):
            return None

        if not user.get("is_active"):
            return None

        # Update last login
        db = await get_db()
        await db.users.update_one(
            {"_id": ObjectId(user["id"])},
            {"$set": {"last_login": datetime.utcnow()}}
        )

        return user

    @staticmethod
    async def update_user(user_id: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Update user information"""
        db = await get_db()

        # Remove sensitive fields
        kwargs.pop("password", None)
        kwargs.pop("email", None)

        # Add updated timestamp
        kwargs["updated_at"] = datetime.utcnow()

        try:
            result = await db.users.find_one_and_update(
                {"_id": ObjectId(user_id)},
                {"$set": kwargs},
                return_document=True
            )
            return UserService._format_user(result) if result else None
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            return None

    @staticmethod
    async def change_password(user_id: str, old_password: str, new_password: str) -> bool:
        """Change user password"""
        db = await get_db()

        try:
            user = await db.users.find_one({"_id": ObjectId(user_id)})
            if not user:
                return False

            # Verify old password
            if not PasswordHasher.verify_password(old_password, user.get("password", "")):
                return False

            # Hash new password
            hashed_password = PasswordHasher.hash_password(new_password)

            # Update password
            await db.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {
                    "password": hashed_password,
                    "updated_at": datetime.utcnow()
                }}
            )

            logger.info(f"Password changed for user: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error changing password: {e}")
            return False

    @staticmethod
    async def delete_user(user_id: str) -> bool:
        """Delete user account"""
        db = await get_db()

        try:
            result = await db.users.delete_one({"_id": ObjectId(user_id)})
            if result.deleted_count > 0:
                logger.info(f"User deleted: {user_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            return False

    @staticmethod
    def _format_user(user: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Format user document for response"""
        if not user:
            return None

        return {
            "id": str(user.get("_id")),
            "email": user.get("email"),
            "full_name": user.get("full_name"),
            "role": user.get("role"),
            "is_active": user.get("is_active"),
            "created_at": user.get("created_at"),
            "last_login": user.get("last_login"),
            "preferences": user.get("preferences", {}),
        }
