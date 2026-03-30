"""
Unit tests for input validation
"""

import pytest
from app.utils.validators import InputValidator, XSSProtection


class TestInputValidator:
    """Test input validation"""

    def test_validate_headline_valid(self):
        """Test valid headline"""
        headline = "This is a valid headline"
        result = InputValidator.validate_headline(headline)
        assert result == headline

    def test_validate_headline_empty(self):
        """Test empty headline"""
        with pytest.raises(ValueError):
            InputValidator.validate_headline("")

    def test_validate_headline_too_short(self):
        """Test headline too short"""
        with pytest.raises(ValueError):
            InputValidator.validate_headline("ab")

    def test_validate_headline_too_long(self):
        """Test headline too long"""
        long_headline = "a" * (InputValidator.MAX_HEADLINE_LENGTH + 1)
        with pytest.raises(ValueError):
            InputValidator.validate_headline(long_headline)

    def test_validate_email_valid(self):
        """Test valid email"""
        email = "test@example.com"
        result = InputValidator.validate_email(email)
        assert result == email

    def test_validate_email_invalid(self):
        """Test invalid email"""
        with pytest.raises(ValueError):
            InputValidator.validate_email("invalid-email")

    def test_validate_password_valid(self):
        """Test valid password"""
        password = "ValidPassword123!"
        result = InputValidator.validate_password(password)
        assert result == password

    def test_validate_password_too_short(self):
        """Test password too short"""
        with pytest.raises(ValueError):
            InputValidator.validate_password("Short1!")

    def test_validate_password_no_uppercase(self):
        """Test password without uppercase"""
        with pytest.raises(ValueError):
            InputValidator.validate_password("lowercase123!")

    def test_validate_image_url_valid(self):
        """Test valid image URL"""
        url = "https://example.com/image.jpg"
        assert InputValidator.validate_image_url(url) is True

    def test_validate_image_url_invalid_extension(self):
        """Test image URL with invalid extension"""
        url = "https://example.com/file.txt"
        assert InputValidator.validate_image_url(url) is False

    def test_validate_file_size_valid(self):
        """Test valid file size"""
        size = 5 * 1024 * 1024  # 5MB
        assert InputValidator.validate_file_size(size) is True

    def test_validate_file_size_too_large(self):
        """Test file size too large"""
        size = 20 * 1024 * 1024  # 20MB
        assert InputValidator.validate_file_size(size) is False

    def test_sanitize_string(self):
        """Test string sanitization"""
        text = "  Test  String  "
        result = InputValidator.sanitize_string(text)
        assert result == "Test  String"

    def test_validate_pagination_valid(self):
        """Test valid pagination"""
        page, limit = InputValidator.validate_pagination(1, 10)
        assert page == 1
        assert limit == 10

    def test_validate_pagination_invalid(self):
        """Test invalid pagination"""
        page, limit = InputValidator.validate_pagination(-1, 200)
        assert page == 1
        assert limit == 100


class TestXSSProtection:
    """Test XSS protection"""

    def test_escape_html(self):
        """Test HTML escaping"""
        text = '<script>alert("xss")</script>'
        result = XSSProtection.escape_html(text)
        assert "<" not in result
        assert ">" not in result

    def test_remove_html_tags(self):
        """Test HTML tag removal"""
        text = '<p>Hello <b>World</b></p>'
        result = XSSProtection.remove_html_tags(text)
        assert "<" not in result
        assert ">" not in result
        assert "Hello World" in result


if __name__ == "__main__":
    pytest.main([__file__])
