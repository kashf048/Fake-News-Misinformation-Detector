"""
Input Validation and Sanitization
Utilities for validating and sanitizing user inputs
"""

import re
from typing import Any
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)


class InputValidator:
    """Input validation utilities"""

    # Constants
    MAX_HEADLINE_LENGTH = 1000
    MIN_HEADLINE_LENGTH = 3
    MAX_EMAIL_LENGTH = 255
    MAX_PASSWORD_LENGTH = 128
    MIN_PASSWORD_LENGTH = 8
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
    ALLOWED_IMAGE_MIMES = {'image/jpeg', 'image/png', 'image/gif', 'image/webp'}

    @staticmethod
    def validate_headline(headline: str) -> str:
        """Validate and sanitize headline"""
        if not headline:
            raise ValueError("Headline cannot be empty")

        headline = headline.strip()

        if len(headline) < InputValidator.MIN_HEADLINE_LENGTH:
            raise ValueError(f"Headline must be at least {InputValidator.MIN_HEADLINE_LENGTH} characters")

        if len(headline) > InputValidator.MAX_HEADLINE_LENGTH:
            raise ValueError(f"Headline cannot exceed {InputValidator.MAX_HEADLINE_LENGTH} characters")

        # Remove excessive whitespace
        headline = re.sub(r'\s+', ' ', headline)

        return headline

    @staticmethod
    def validate_email(email: str) -> str:
        """Validate email address"""
        if not email:
            raise ValueError("Email cannot be empty")

        email = email.strip().lower()

        if len(email) > InputValidator.MAX_EMAIL_LENGTH:
            raise ValueError("Email is too long")

        # RFC 5322 simplified regex
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            raise ValueError("Invalid email format")

        return email

    @staticmethod
    def validate_password(password: str) -> str:
        """Validate password strength"""
        if not password:
            raise ValueError("Password cannot be empty")

        if len(password) < InputValidator.MIN_PASSWORD_LENGTH:
            raise ValueError(f"Password must be at least {InputValidator.MIN_PASSWORD_LENGTH} characters")

        if len(password) > InputValidator.MAX_PASSWORD_LENGTH:
            raise ValueError("Password is too long")

        # Check for complexity
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password)

        if not (has_upper and has_lower and has_digit):
            raise ValueError(
                "Password must contain uppercase, lowercase, and digits"
            )

        return password

    @staticmethod
    def validate_image_url(url: str) -> bool:
        """Validate image URL"""
        if not url:
            return False

        url = url.strip()

        try:
            result = urlparse(url)
            if not all([result.scheme, result.netloc]):
                return False

            if result.scheme not in ['http', 'https']:
                return False

            # Check file extension
            path = result.path.lower()
            for ext in InputValidator.ALLOWED_IMAGE_EXTENSIONS:
                if path.endswith(f'.{ext}'):
                    return True

            return False
        except Exception as e:
            logger.error(f"Error validating URL: {e}")
            return False

    @staticmethod
    def validate_file_size(size: int) -> bool:
        """Validate file size"""
        return 0 < size <= InputValidator.MAX_FILE_SIZE

    @staticmethod
    def validate_mime_type(mime_type: str) -> bool:
        """Validate MIME type"""
        return mime_type in InputValidator.ALLOWED_IMAGE_MIMES

    @staticmethod
    def sanitize_string(text: str) -> str:
        """Sanitize string input"""
        if not isinstance(text, str):
            return ""

        # Remove null bytes
        text = text.replace('\x00', '')

        # Remove control characters
        text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')

        # Trim whitespace
        text = text.strip()

        return text

    @staticmethod
    def validate_pagination(page: int, limit: int) -> tuple:
        """Validate pagination parameters"""
        if page < 1:
            page = 1

        if limit < 1:
            limit = 10

        if limit > 100:
            limit = 100

        return page, limit

    @staticmethod
    def validate_filter(filter_value: str) -> str:
        """Validate filter value"""
        allowed_values = ['Fake', 'Real', 'Misleading']

        if filter_value not in allowed_values:
            raise ValueError(f"Invalid filter value. Must be one of: {', '.join(allowed_values)}")

        return filter_value


class XSSProtection:
    """XSS protection utilities"""

    @staticmethod
    def escape_html(text: str) -> str:
        """Escape HTML special characters"""
        if not isinstance(text, str):
            return ""

        escape_map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#x27;',
        }

        for char, escaped in escape_map.items():
            text = text.replace(char, escaped)

        return text

    @staticmethod
    def remove_html_tags(text: str) -> str:
        """Remove HTML tags from text"""
        if not isinstance(text, str):
            return ""

        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)

        # Decode HTML entities
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&quot;', '"')
        text = text.replace('&#x27;', "'")
        text = text.replace('&amp;', '&')

        return text


class SQLInjectionProtection:
    """SQL Injection protection (for reference, using MongoDB)"""

    @staticmethod
    def validate_query_param(param: str) -> str:
        """Validate query parameter"""
        if not isinstance(param, str):
            return ""

        # Remove potentially dangerous characters
        dangerous_chars = [';', '--', '/*', '*/', 'xp_', 'sp_']
        for char in dangerous_chars:
            if char.lower() in param.lower():
                raise ValueError(f"Invalid query parameter")

        return param
