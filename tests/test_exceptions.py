"""
Tests for exceptions.
"""

from mtn_cloud.exceptions import (
    AuthenticationError,
    ForbiddenError,
    MTNCloudError,
    NotFoundError,
    QuotaExceededError,
    RateLimitError,
    ServerError,
    TimeoutError,
    ValidationError,
)


class TestMTNCloudError:
    """Tests for base exception."""

    def test_basic_error(self):
        """Test basic error creation."""
        error = MTNCloudError("Something went wrong")
        assert str(error) == "Something went wrong"
        assert error.message == "Something went wrong"
        assert error.status_code is None

    def test_error_with_status_code(self):
        """Test error with status code."""
        error = MTNCloudError("Error", status_code=500)
        assert "(HTTP 500)" in str(error)
        assert error.status_code == 500

    def test_error_with_request_id(self):
        """Test error with request ID."""
        error = MTNCloudError("Error", request_id="req-123")
        assert "[Request ID: req-123]" in str(error)

    def test_error_repr(self):
        """Test error repr."""
        error = MTNCloudError("Error", status_code=500)
        repr_str = repr(error)
        assert "MTNCloudError" in repr_str
        assert "500" in repr_str


class TestAuthenticationError:
    """Tests for authentication errors."""

    def test_default_message(self):
        """Test default error message."""
        error = AuthenticationError()
        assert "Authentication failed" in str(error)
        assert error.status_code == 401

    def test_custom_message(self):
        """Test custom message."""
        error = AuthenticationError("Token expired")
        assert "Token expired" in str(error)


class TestNotFoundError:
    """Tests for not found errors."""

    def test_default_message(self):
        """Test default error message."""
        error = NotFoundError()
        assert error.status_code == 404

    def test_with_resource_info(self):
        """Test with resource type and ID."""
        error = NotFoundError(resource_type="Instance", resource_id=123)
        assert "Instance" in str(error)
        assert "123" in str(error)


class TestValidationError:
    """Tests for validation errors."""

    def test_default_message(self):
        """Test default error message."""
        error = ValidationError()
        assert error.status_code == 400

    def test_with_errors_list(self):
        """Test with validation errors list."""
        errors = [
            {"field": "name", "message": "required"},
            {"field": "email", "message": "invalid format"},
        ]
        error = ValidationError(errors=errors)
        assert "name" in str(error)
        assert "email" in str(error)


class TestForbiddenError:
    """Tests for forbidden errors."""

    def test_default_message(self):
        """Test default error message."""
        error = ForbiddenError()
        assert "forbidden" in str(error).lower()
        assert error.status_code == 403


class TestRateLimitError:
    """Tests for rate limit errors."""

    def test_default_message(self):
        """Test default error message."""
        error = RateLimitError()
        assert error.status_code == 429

    def test_with_retry_after(self):
        """Test with retry after value."""
        error = RateLimitError(retry_after=60)
        assert error.retry_after == 60
        assert "60" in str(error)


class TestServerError:
    """Tests for server errors."""

    def test_default_message(self):
        """Test default error message."""
        error = ServerError()
        assert error.status_code == 500

    def test_custom_status_code(self):
        """Test with custom status code."""
        error = ServerError(status_code=503)
        assert error.status_code == 503


class TestTimeoutError:
    """Tests for timeout errors."""

    def test_with_timeout_value(self):
        """Test with timeout value."""
        error = TimeoutError(timeout=30.0)
        assert error.timeout == 30.0
        assert "30" in str(error)


class TestQuotaExceededError:
    """Tests for quota exceeded errors."""

    def test_default_message(self):
        """Test default error message."""
        error = QuotaExceededError()
        assert "quota" in str(error).lower()

    def test_with_quota_info(self):
        """Test with quota information."""
        error = QuotaExceededError(
            quota_type="instances",
            current=10,
            limit=10,
        )
        assert "instances" in str(error)
        assert "10/10" in str(error)
