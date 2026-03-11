"""
MTN Cloud SDK Exceptions
========================

Custom exception classes for the MTN Cloud SDK.
All exceptions inherit from MTNCloudError for easy catching.

Example:
    ```python
    from mtn_cloud import MTNCloud, MTNCloudError, NotFoundError

    cloud = MTNCloud(token="xxx")

    try:
        instance = cloud.instances.get(999999)
    except NotFoundError as e:
        print(f"Instance not found: {e}")
    except MTNCloudError as e:
        print(f"API error: {e}")
    ```
"""

from typing import Any


class MTNCloudError(Exception):
    """
    Base exception for all MTN Cloud SDK errors.

    Attributes:
        message: Human-readable error message
        status_code: HTTP status code (if applicable)
        response: Raw API response (if available)
        request_id: API request ID for debugging
    """

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response: dict[str, Any] | None = None,
        request_id: str | None = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.response = response
        self.request_id = request_id
        super().__init__(self.message)

    def __str__(self) -> str:
        parts = [self.message]
        if self.status_code:
            parts.append(f"(HTTP {self.status_code})")
        if self.request_id:
            parts.append(f"[Request ID: {self.request_id}]")
        return " ".join(parts)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"message={self.message!r}, "
            f"status_code={self.status_code}, "
            f"request_id={self.request_id!r})"
        )


class AuthenticationError(MTNCloudError):
    """
    Raised when authentication fails.

    Common causes:
    - Invalid or expired token
    - Missing authentication credentials
    - Token revoked
    """

    def __init__(
        self,
        message: str = "Authentication failed. Check your API token.",
        **kwargs: Any,
    ) -> None:
        super().__init__(message, status_code=401, **kwargs)


class ForbiddenError(MTNCloudError):
    """
    Raised when access to a resource is forbidden.

    Common causes:
    - Insufficient permissions
    - Resource belongs to another user/tenant
    - Endpoint not available on MTN Cloud
    """

    def __init__(
        self,
        message: str = "Access forbidden. You don't have permission for this resource.",
        **kwargs: Any,
    ) -> None:
        super().__init__(message, status_code=403, **kwargs)


class NotFoundError(MTNCloudError):
    """
    Raised when a requested resource is not found.

    Common causes:
    - Invalid resource ID
    - Resource was deleted
    - Typo in resource name
    """

    def __init__(
        self,
        message: str = "Resource not found.",
        resource_type: str | None = None,
        resource_id: Any | None = None,
        **kwargs: Any,
    ) -> None:
        if resource_type and resource_id:
            message = f"{resource_type} with ID '{resource_id}' not found."
        elif resource_type:
            message = f"{resource_type} not found."

        self.resource_type = resource_type
        self.resource_id = resource_id
        super().__init__(message, status_code=404, **kwargs)


class ValidationError(MTNCloudError):
    """
    Raised when request validation fails.

    Common causes:
    - Missing required fields
    - Invalid field values
    - Constraint violations
    """

    def __init__(
        self,
        message: str = "Validation error.",
        errors: list[Any] | dict[str, Any] | str | None = None,
        **kwargs: Any,
    ) -> None:
        if errors is None:
            normalized_errors: list[Any] = []
        elif isinstance(errors, list):
            normalized_errors = errors
        else:
            normalized_errors = [errors]

        self.errors = normalized_errors
        if self.errors:
            error_parts: list[str] = []
            for error in self.errors:
                if isinstance(error, dict):
                    field = (
                        error.get("field") or error.get("name") or error.get("path") or "unknown"
                    )
                    error_message = (
                        error.get("message") or error.get("msg") or error.get("error") or "invalid"
                    )
                    error_parts.append(f"{field}: {error_message}")
                else:
                    error_parts.append(str(error))

            error_details = "; ".join(error_parts)
            message = f"{message} {error_details}"
        super().__init__(message, status_code=400, **kwargs)


class RateLimitError(MTNCloudError):
    """
    Raised when API rate limit is exceeded.

    Attributes:
        retry_after: Seconds to wait before retrying
    """

    def __init__(
        self,
        message: str = "Rate limit exceeded. Please slow down.",
        retry_after: int | None = None,
        **kwargs: Any,
    ) -> None:
        self.retry_after = retry_after
        if retry_after:
            message = f"{message} Retry after {retry_after} seconds."
        super().__init__(message, status_code=429, **kwargs)


class ServerError(MTNCloudError):
    """
    Raised when the server encounters an error.

    Common causes:
    - Internal server error
    - Service temporarily unavailable
    - Upstream dependency failure
    """

    def __init__(
        self,
        message: str = "Server error. Please try again later.",
        **kwargs: Any,
    ) -> None:
        status_code = kwargs.pop("status_code", 500)
        super().__init__(message, status_code=status_code, **kwargs)


class TimeoutError(MTNCloudError):
    """
    Raised when a request times out.

    Common causes:
    - Network issues
    - Server overloaded
    - Long-running operation
    """

    def __init__(
        self,
        message: str = "Request timed out.",
        timeout: float | None = None,
        **kwargs: Any,
    ) -> None:
        self.timeout = timeout
        if timeout:
            message = f"{message} (timeout: {timeout}s)"
        super().__init__(message, **kwargs)


class ResourceConflictError(MTNCloudError):
    """
    Raised when there's a conflict with the current resource state.

    Common causes:
    - Resource already exists
    - Concurrent modification
    - Invalid state transition
    """

    def __init__(
        self,
        message: str = "Resource conflict.",
        **kwargs: Any,
    ) -> None:
        super().__init__(message, status_code=409, **kwargs)


class QuotaExceededError(MTNCloudError):
    """
    Raised when a quota or limit is exceeded.

    Common causes:
    - Instance limit reached
    - Storage quota exceeded
    - IP address limit reached
    """

    def __init__(
        self,
        message: str = "Quota exceeded.",
        quota_type: str | None = None,
        current: int | None = None,
        limit: int | None = None,
        **kwargs: Any,
    ) -> None:
        self.quota_type = quota_type
        self.current = current
        self.limit = limit

        if quota_type and current is not None and limit is not None:
            message = f"{quota_type} quota exceeded: {current}/{limit}"
        elif quota_type:
            message = f"{quota_type} quota exceeded."

        super().__init__(message, status_code=402, **kwargs)
