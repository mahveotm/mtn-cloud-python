"""Low-level HTTP transport, authentication, and error mapping."""

import logging
import math
from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any, Literal

import requests
from pydantic import SecretStr
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from mtn_cloud.config import MTNCloudConfig
from mtn_cloud.exceptions import (
    AuthenticationError,
    ForbiddenError,
    MTNCloudError,
    NotFoundError,
    QuotaExceededError,
    RateLimitError,
    ResourceConflictError,
    ServerError,
    ValidationError,
)
from mtn_cloud.exceptions import (
    TimeoutError as MTNTimeoutError,
)

logger = logging.getLogger("mtn_cloud.http")

HTTPMethod = Literal["GET", "POST", "PUT", "PATCH", "DELETE"]
SAFE_RETRY_METHODS = frozenset({"GET", "HEAD", "OPTIONS"})
REDACTED = "<redacted>"
MAX_LOG_VALUE_LENGTH = 4_096

_SENSITIVE_KEY_FRAGMENTS = (
    "accesskey",
    "accesstoken",
    "apikey",
    "authorization",
    "cookie",
    "credential",
    "password",
    "passwd",
    "privatekey",
    "secret",
    "token",
)


def _is_sensitive_key(key: Any) -> bool:
    """Return whether a mapping key conventionally contains secret material."""
    normalized = "".join(character for character in str(key).lower() if character.isalnum())
    return any(fragment in normalized for fragment in _SENSITIVE_KEY_FRAGMENTS)


def _redact_sensitive(value: Any, *, known_secrets: Sequence[str] = ()) -> Any:
    """Recursively redact secret fields and known secret values."""
    if isinstance(value, SecretStr):
        return REDACTED
    if isinstance(value, Mapping):
        return {
            key: REDACTED
            if _is_sensitive_key(key)
            else _redact_sensitive(item, known_secrets=known_secrets)
            for key, item in value.items()
        }
    if isinstance(value, list | tuple | set | frozenset):
        return [_redact_sensitive(item, known_secrets=known_secrets) for item in value]
    if isinstance(value, bytes):
        return f"<bytes:{len(value)}>"
    if isinstance(value, str):
        redacted = value
        for secret in sorted({secret for secret in known_secrets if secret}, key=len, reverse=True):
            redacted = redacted.replace(secret, REDACTED)
        return redacted
    return value


class HTTPClient:
    """
    Low-level HTTP client for MTN Cloud API.

    Handles:
    - Authentication (token and username/password)
    - Automatic retries with exponential backoff
    - Error mapping to specific exceptions
    - Request/response logging

    This is an internal class. Use MTNCloud client instead.
    """

    def __init__(self, config: MTNCloudConfig) -> None:
        """
        Initialize the HTTP client.

        Args:
            config: SDK configuration
        """
        self.config = config
        self._session: requests.Session | None = None
        self._token: str | None = None

        if config.token:
            self._token = config.get_token_value()

    @property
    def session(self) -> requests.Session:
        """Get or create the requests' session."""
        if self._session is None:
            self._session = self._create_session()
        return self._session

    def _create_session(self) -> requests.Session:
        """Create a configured requests session with retry logic."""
        session = requests.Session()

        retry_strategy = Retry(
            total=self.config.max_retries,
            backoff_factor=self.config.retry_delay,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=SAFE_RETRY_METHODS,
            respect_retry_after_header=True,
            raise_on_status=False,
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        session.headers.update(
            {
                "Accept": "application/json",
                "User-Agent": self.config.user_agent,
            }
        )

        session.verify = self.config.verify_ssl

        return session

    def authenticate(self) -> str:
        """
        Authenticate and obtain an access token.

        Uses username/password OAuth flow if no token is configured.

        Returns:
            Access token

        Raises:
            AuthenticationError: If authentication fails
        """
        if self._token:
            return self._token

        if not self.config.username or not self.config.password:
            raise AuthenticationError(
                "No authentication credentials configured. "
                "Provide either a token or username/password."
            )

        oauth_url = f"{self.config.url}/oauth/token"
        params = {
            "grant_type": "password",
            "scope": "write",
            "client_id": "morph-cli",
        }
        data = {
            "username": self.config.username,
            "password": self.config.get_password_value(),
        }

        try:
            response = self.session.post(
                oauth_url,
                params=params,
                data=data,
                timeout=self.config.timeout,
            )

            if response.status_code != 200:
                response_payload = self._parse_response_body(response)
                safe_payload = self._redact(response_payload)
                raise AuthenticationError(
                    self._extract_error_message(safe_payload),
                    status_code=response.status_code,
                    response=safe_payload,
                )

            try:
                result = response.json()
                token = result["access_token"]
                if not isinstance(token, str) or not token:
                    raise ValueError("access_token must be a non-empty string")
            except (KeyError, TypeError, ValueError) as exc:
                safe_payload = self._redact(self._parse_response_body(response))
                raise AuthenticationError(
                    "Authentication response did not contain a valid access token.",
                    status_code=response.status_code,
                    response=safe_payload,
                ) from exc
            self._token = token

            logger.debug("Successfully authenticated")
            return token

        except requests.exceptions.RequestException as e:
            raise AuthenticationError(f"Authentication request failed: {e}") from e

    def _get_headers(self) -> dict[str, str]:
        """Get request headers with authentication."""
        token = self.authenticate()
        return {
            "Authorization": f"Bearer {token}",
        }

    def request(
        self,
        method: HTTPMethod,
        path: str,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        files: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> dict[str, Any]:
        """
        Make an HTTP request to the MTN Cloud API.

        Args:
            method: HTTP method
            path: API path (will be joined with base URL)
            params: Query parameters
            json: JSON body
            data: Form data
            files: Multipart file payload
            headers: Additional headers
            timeout: Request timeout override

        Returns:
            JSON response as dictionary

        Raises:
            MTNCloudError: On API errors
            AuthenticationError: On 401 responses
            ForbiddenError: On 403 responses
            NotFoundError: On 404 responses
            ValidationError: On 400 responses
            RateLimitError: On 429 responses
            ServerError: On 5xx responses
        """
        url = self._build_url(path)
        request_headers = {**self._get_headers(), **(headers or {})}
        request_timeout = timeout if timeout is not None else self.config.timeout

        if self.config.debug:
            logger.debug("Request: %s %s", method, url)
            if params:
                logger.debug("Params: %s", self._format_for_log(params))
            if json:
                logger.debug("JSON: %s", self._format_for_log(json))
            if data:
                logger.debug("Data: %s", self._format_for_log(data))
            if files:
                logger.debug("Multipart fields: %s", sorted(files))

        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=json,
                data=data,
                files=files,
                headers=request_headers,
                timeout=request_timeout,
            )

            return self._handle_response(response)

        except requests.exceptions.Timeout as e:
            raise MTNTimeoutError(
                f"Request to {path} timed out",
                timeout=request_timeout,
            ) from e
        except requests.exceptions.ConnectionError as e:
            raise MTNCloudError(f"Connection error: {e}") from e
        except requests.exceptions.RequestException as e:
            raise MTNCloudError(f"Request failed: {e}") from e

    def _build_url(self, path: str) -> str:
        """Build full URL from path."""
        if not path.startswith("/"):
            path = "/" + path
        return f"{self.config.api_url}{path}"

    def _handle_response(self, response: requests.Response) -> dict[str, Any]:
        """
        Handle API response and raise appropriate exceptions.

        Args:
            response: requests Response object

        Returns:
            Parsed JSON response

        Raises:
            Appropriate MTNCloudError subclass based on status code
        """
        request_id = response.headers.get("X-Request-Id")

        body = self._parse_response_body(response)

        if self.config.debug:
            logger.debug("Response: %s", response.status_code)
            logger.debug("Body: %s", self._format_for_log(body))

        if 200 <= response.status_code < 300:
            return body

        safe_body = self._redact(body)
        error_message = self._extract_error_message(safe_body)
        status_code = response.status_code

        if status_code == 400:
            errors = safe_body.get("errors", [])
            raise ValidationError(
                message=error_message,
                errors=errors,
                response=safe_body,
                request_id=request_id,
            )

        if status_code == 401:
            if self.config.username and self.config.password:
                self._token = None
            raise AuthenticationError(
                message=error_message,
                status_code=status_code,
                response=safe_body,
                request_id=request_id,
            )

        if status_code == 403:
            raise ForbiddenError(
                message=error_message,
                response=safe_body,
                request_id=request_id,
            )

        if status_code == 404:
            raise NotFoundError(
                message=error_message,
                response=safe_body,
                request_id=request_id,
            )

        if status_code == 402:
            raise QuotaExceededError(
                message=error_message,
                quota_type=safe_body.get("quotaType") or safe_body.get("quota"),
                current=(
                    safe_body.get("current") if isinstance(safe_body.get("current"), int) else None
                ),
                limit=(safe_body.get("limit") if isinstance(safe_body.get("limit"), int) else None),
                response=safe_body,
                request_id=request_id,
            )

        if status_code == 409:
            raise ResourceConflictError(
                message=error_message,
                response=safe_body,
                request_id=request_id,
            )

        if status_code == 429:
            retry_after = self._parse_retry_after(response.headers.get("Retry-After"))
            raise RateLimitError(
                message=error_message,
                retry_after=retry_after,
                response=safe_body,
                request_id=request_id,
            )

        if status_code >= 500:
            raise ServerError(
                message=error_message,
                status_code=status_code,
                response=safe_body,
                request_id=request_id,
            )

        raise MTNCloudError(
            message=error_message,
            status_code=status_code,
            response=safe_body,
            request_id=request_id,
        )

    def _extract_error_message(self, body: dict[str, Any]) -> str:
        """Extract human-readable error message from response body."""
        for field in ["message", "msg", "error", "error_description"]:
            if field in body and body[field]:
                return str(body[field])

        if "errors" in body and isinstance(body["errors"], list):
            messages = [e.get("message", str(e)) for e in body["errors"] if isinstance(e, dict)]
            if messages:
                return "; ".join(messages)

        if "errors" in body and isinstance(body["errors"], dict):
            field_messages: list[str] = []
            for field, value in body["errors"].items():
                if isinstance(value, list):
                    joined = ", ".join(str(item) for item in value)
                    field_messages.append(f"{field}: {joined}")
                elif isinstance(value, dict):
                    detail = value.get("message") or value.get("msg") or str(value)
                    field_messages.append(f"{field}: {detail}")
                else:
                    field_messages.append(f"{field}: {value}")
            if field_messages:
                return "; ".join(field_messages)

        if body:
            return str(body)

        return "Unknown error"

    def _known_secrets(self) -> tuple[str, ...]:
        """Return configured secret values for value-based redaction."""
        return tuple(
            secret
            for secret in (
                self._token,
                self.config.get_token_value(),
                self.config.get_password_value(),
            )
            if secret
        )

    def _redact(self, value: Any) -> Any:
        """Redact configured and conventionally named secrets."""
        return _redact_sensitive(value, known_secrets=self._known_secrets())

    def _format_for_log(self, value: Any) -> str:
        """Return a bounded, redacted representation suitable for debug logs."""
        formatted = repr(self._redact(value))
        if len(formatted) <= MAX_LOG_VALUE_LENGTH:
            return formatted
        return f"{formatted[:MAX_LOG_VALUE_LENGTH]}... <truncated>"

    def _parse_response_body(self, response: requests.Response) -> dict[str, Any]:
        """Normalize JSON bodies and safely describe non-JSON API errors."""
        if not response.text:
            return {}

        try:
            parsed = response.json()
        except ValueError:
            if 200 <= response.status_code < 300:
                return {"raw": response.text}

            content_type = response.headers.get("Content-Type", "unknown content type")
            return {
                "message": (
                    f"Non-JSON response from API (HTTP {response.status_code}, {content_type})"
                ),
                "contentType": content_type,
                "contentLength": len(response.content),
            }

        if isinstance(parsed, dict):
            return parsed
        return {"data": parsed}

    @staticmethod
    def _parse_retry_after(
        value: str | None,
        *,
        now: datetime | None = None,
    ) -> int | None:
        """Parse Retry-After delta-seconds or an HTTP date into whole seconds."""
        if not value:
            return None

        normalized = value.strip()
        try:
            return max(0, int(normalized))
        except ValueError:
            pass

        try:
            retry_at = parsedate_to_datetime(normalized)
        except (TypeError, ValueError, OverflowError):
            return None

        if retry_at.tzinfo is None:
            retry_at = retry_at.replace(tzinfo=timezone.utc)
        reference = now or datetime.now(timezone.utc)
        if reference.tzinfo is None:
            reference = reference.replace(tzinfo=timezone.utc)
        return max(0, math.ceil((retry_at - reference).total_seconds()))

    # Convenience methods
    def get(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Make a GET request."""
        return self.request("GET", path, params=params, **kwargs)

    def post(
        self,
        path: str,
        json: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Make a POST request."""
        return self.request("POST", path, json=json, **kwargs)

    def put(
        self,
        path: str,
        json: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Make a PUT request."""
        return self.request("PUT", path, json=json, **kwargs)

    def patch(
        self,
        path: str,
        json: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Make a PATCH request."""
        return self.request("PATCH", path, json=json, **kwargs)

    def delete(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Make a DELETE request."""
        return self.request("DELETE", path, params=params, **kwargs)

    def get_bytes(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> bytes:
        """
        Make a GET request and return raw bytes.

        Useful for binary file download endpoints.
        """
        url = self._build_url(path)
        request_headers = {**self._get_headers(), **(headers or {})}
        request_timeout = timeout if timeout is not None else self.config.timeout

        try:
            response = self.session.request(
                method="GET",
                url=url,
                params=params,
                headers=request_headers,
                timeout=request_timeout,
            )

            if 200 <= response.status_code < 300:
                return response.content

            # Reuse standard error mapping.
            self._handle_response(response)
            return b""
        except requests.exceptions.Timeout as e:
            raise MTNTimeoutError(
                f"Request to {path} timed out",
                timeout=request_timeout,
            ) from e
        except requests.exceptions.ConnectionError as e:
            raise MTNCloudError(f"Connection error: {e}") from e
        except requests.exceptions.RequestException as e:
            raise MTNCloudError(f"Request failed: {e}") from e

    def close(self) -> None:
        """Close the HTTP session."""
        if self._session:
            self._session.close()
            self._session = None

    def __enter__(self) -> "HTTPClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
