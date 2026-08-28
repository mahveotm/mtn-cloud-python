"""Tests for HTTP transport security, retries, and response handling."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from email.utils import format_datetime
from unittest.mock import MagicMock

import pytest
import requests

from mtn_cloud.config import DEFAULT_USER_AGENT, MTNCloudConfig
from mtn_cloud.exceptions import (
    AuthenticationError,
    ForbiddenError,
    MTNCloudError,
    NotFoundError,
    QuotaExceededError,
    RateLimitError,
    ResourceConflictError,
    ServerError,
    TimeoutError,
    ValidationError,
)
from mtn_cloud.http import REDACTED, SAFE_RETRY_METHODS, HTTPClient


def response(
    status: int,
    body: object | str | None = None,
    *,
    content_type: str = "application/json",
    headers: dict[str, str] | None = None,
) -> requests.Response:
    """Build a concrete requests response for transport tests."""
    result = requests.Response()
    result.status_code = status
    if body is None:
        result._content = b""
    elif content_type == "application/json":
        result._content = json.dumps(body).encode()
    else:
        result._content = str(body).encode()
    result.headers["Content-Type"] = content_type
    result.headers.update(headers or {})
    return result


def client_with_response(
    result: requests.Response,
    *,
    debug: bool = False,
    password: str | None = None,
) -> tuple[HTTPClient, MagicMock]:
    """Build a token-authenticated client around a mocked session."""
    config = MTNCloudConfig(
        token="configured-token",
        username="test-user" if password else None,
        password=password,
        debug=debug,
    )
    client = HTTPClient(config)
    session = MagicMock()
    session.request.return_value = result
    client._session = session
    return client, session


class TestRetryConfiguration:
    """Retry only operations that are safe to replay."""

    def test_only_idempotent_methods_are_status_retried(self) -> None:
        client = HTTPClient(MTNCloudConfig(token="test"))

        retries = client.session.get_adapter("https://").max_retries

        assert retries.allowed_methods == SAFE_RETRY_METHODS
        assert "POST" not in retries.allowed_methods
        assert "PUT" not in retries.allowed_methods
        assert "PATCH" not in retries.allowed_methods
        assert "DELETE" not in retries.allowed_methods

    def test_retry_settings_are_preserved(self) -> None:
        client = HTTPClient(MTNCloudConfig(token="test", max_retries=5, retry_delay=1.5))

        retries = client.session.get_adapter("https://").max_retries

        assert retries.total == 5
        assert retries.backoff_factor == 1.5
        assert retries.respect_retry_after_header is True


class TestUserAgent:
    """Preserve the user agent accepted by the MTN API edge."""

    def test_default_user_agent_is_sent(self) -> None:
        client = HTTPClient(MTNCloudConfig(token="test"))

        assert client.session.headers["User-Agent"] == DEFAULT_USER_AGENT

    def test_custom_identity_is_appended(self) -> None:
        client = HTTPClient(MTNCloudConfig(token="test", user_agent="example-app/2.0"))

        assert client.session.headers["User-Agent"] == f"{DEFAULT_USER_AGENT} example-app/2.0"


class TestSecretHandling:
    """Keep credentials out of logs and raised exception payloads."""

    def test_debug_logs_recursively_redact_requests_and_responses(
        self,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        result = response(
            200,
            {
                "storageBucket": {
                    "accessKey": "response-access-key",
                    "config": {
                        "secretKeyHashHash": "response-secret-hash",
                        "windowsPassword": "response-password",
                    },
                }
            },
        )
        client, _ = client_with_response(result, debug=True, password="configured-password")
        caplog.set_level(logging.DEBUG, logger="mtn_cloud.http")

        returned = client.request(
            "POST",
            "/storage-buckets",
            params={"apiToken": "query-token"},
            json={
                "accessKey": "request-access-key",
                "config": {"secretKey": "request-secret-key"},
                "description": "contains configured-token and configured-password",
            },
            data={"password": "form-password"},
        )

        logs = caplog.text
        for secret in (
            "configured-token",
            "configured-password",
            "query-token",
            "request-access-key",
            "request-secret-key",
            "form-password",
            "response-access-key",
            "response-secret-hash",
            "response-password",
        ):
            assert secret not in logs
        assert REDACTED in logs
        assert returned["storageBucket"]["accessKey"] == "response-access-key"

    def test_error_response_is_redacted_before_exposure(self) -> None:
        result = response(
            400,
            {
                "message": "Invalid configured-token",
                "secretKey": "response-secret",
                "errors": [{"field": "password", "message": "bad configured-password"}],
            },
        )
        client, _ = client_with_response(result, password="configured-password")

        with pytest.raises(ValidationError) as captured:
            client.get("/bad-request")

        error = captured.value
        assert "configured-token" not in str(error)
        assert "configured-password" not in str(error)
        assert error.response is not None
        assert error.response["secretKey"] == REDACTED
        assert error.response["errors"][0]["message"] == f"bad {REDACTED}"

    def test_password_authentication_unwraps_secret_only_for_request(self) -> None:
        config = MTNCloudConfig(username="test-user", password="password-value")
        client = HTTPClient(config)
        session = MagicMock()
        session.post.return_value = response(200, {"access_token": "new-token"})
        client._session = session

        assert client.authenticate() == "new-token"
        assert "password-value" not in repr(config)
        assert session.post.call_args.kwargs["data"]["password"] == "password-value"

    def test_invalid_authentication_payload_has_safe_error(self) -> None:
        config = MTNCloudConfig(username="test-user", password="password-value")
        client = HTTPClient(config)
        session = MagicMock()
        session.post.return_value = response(200, {"message": "missing token"})
        client._session = session

        with pytest.raises(AuthenticationError, match="valid access token"):
            client.authenticate()


class TestResponseHandling:
    """Normalize API responses without leaking edge-generated HTML."""

    def test_non_json_error_is_described_without_body(self) -> None:
        html = "<html><body>edge rejection with configured-token</body></html>"
        client, _ = client_with_response(response(403, html, content_type="text/html"))

        with pytest.raises(ForbiddenError) as captured:
            client.get("/blocked")

        error = captured.value
        assert str(error).startswith("Non-JSON response from API (HTTP 403, text/html)")
        assert html not in str(error)
        assert error.response == {
            "message": "Non-JSON response from API (HTTP 403, text/html)",
            "contentType": "text/html",
            "contentLength": len(html.encode()),
        }

    def test_successful_json_list_is_normalized(self) -> None:
        client, _ = client_with_response(response(200, [{"id": 1}]))

        assert client.get("/items") == {"data": [{"id": 1}]}

    def test_successful_non_json_response_remains_available(self) -> None:
        client, _ = client_with_response(response(200, "plain text", content_type="text/plain"))

        assert client.get("/text") == {"raw": "plain text"}

    def test_empty_success_response_is_an_empty_mapping(self) -> None:
        client, _ = client_with_response(response(204))

        assert client.delete("/items/1") == {}

    @pytest.mark.parametrize(
        ("status", "body", "error_type"),
        [
            (401, {"message": "expired"}, AuthenticationError),
            (403, {"message": "forbidden"}, ForbiddenError),
            (404, {"message": "missing"}, NotFoundError),
            (409, {"message": "conflict"}, ResourceConflictError),
            (500, {"message": "failed"}, ServerError),
            (418, {"message": "unexpected"}, MTNCloudError),
        ],
    )
    def test_status_code_exception_mapping(
        self,
        status: int,
        body: dict[str, str],
        error_type: type[MTNCloudError],
    ) -> None:
        client, _ = client_with_response(response(status, body))

        with pytest.raises(error_type) as captured:
            client.get("/resource")

        assert captured.value.status_code == status

    def test_quota_response_populates_structured_fields(self) -> None:
        client, _ = client_with_response(
            response(
                402,
                {"message": "quota exceeded", "quotaType": "instances", "current": 5, "limit": 5},
            )
        )

        with pytest.raises(QuotaExceededError) as captured:
            client.post("/instances")

        assert captured.value.quota_type == "instances"
        assert captured.value.current == 5
        assert captured.value.limit == 5

    def test_explicit_request_timeout_is_forwarded(self) -> None:
        client, session = client_with_response(response(200, {}))

        client.get("/resource", timeout=7.5)

        assert session.request.call_args.kwargs["timeout"] == 7.5

    def test_request_timeout_is_mapped(self) -> None:
        client, session = client_with_response(response(200, {}))
        session.request.side_effect = requests.exceptions.Timeout("slow")

        with pytest.raises(TimeoutError) as captured:
            client.get("/slow", timeout=7.5)

        assert captured.value.timeout == 7.5

    def test_connection_error_is_mapped(self) -> None:
        client, session = client_with_response(response(200, {}))
        session.request.side_effect = requests.exceptions.ConnectionError("offline")

        with pytest.raises(MTNCloudError, match="Connection error"):
            client.get("/offline")

    def test_get_bytes_returns_binary_content(self) -> None:
        result = response(200)
        result._content = b"binary-content"
        client, _ = client_with_response(result)

        assert client.get_bytes("/archive/file") == b"binary-content"

    def test_get_bytes_reuses_error_mapping(self) -> None:
        client, _ = client_with_response(response(404, {"message": "missing"}))

        with pytest.raises(NotFoundError):
            client.get_bytes("/archive/missing")


class TestRetryAfter:
    """Support both HTTP forms of Retry-After."""

    @pytest.mark.parametrize(
        ("value", "expected"),
        [("120", 120), ("0", 0), ("-5", 0), ("invalid", None), (None, None)],
    )
    def test_parse_delta_or_invalid_value(self, value: str | None, expected: int | None) -> None:
        assert HTTPClient._parse_retry_after(value) == expected

    def test_parse_http_date(self) -> None:
        now = datetime(2026, 8, 28, 12, 0, 0, tzinfo=timezone.utc)
        retry_at = datetime(2026, 8, 28, 12, 1, 1, tzinfo=timezone.utc)

        assert HTTPClient._parse_retry_after(format_datetime(retry_at), now=now) == 61

    def test_rate_limit_exception_uses_parsed_header(self) -> None:
        result = response(429, {"message": "slow down"}, headers={"Retry-After": "120"})
        client, _ = client_with_response(result)

        with pytest.raises(RateLimitError) as captured:
            client.get("/limited")

        assert captured.value.retry_after == 120
