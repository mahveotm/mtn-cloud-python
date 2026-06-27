"""Tests for security group models and resources."""

from typing import Any
from unittest.mock import MagicMock

import pytest

from mtn_cloud.exceptions import NotFoundError
from mtn_cloud.models.security_group import (
    SecurityGroupCreate,
    SecurityGroupRuleCreate,
    SecurityGroupRuleUpdate,
    SecurityGroupUpdate,
)
from mtn_cloud.resources.security_groups import SecurityGroupsResource

from .conftest import nested_value

SAMPLE_RULE = {
    "id": 90,
    "name": "allow-ssh",
    "direction": "ingress",
    "policy": "accept",
    "sourceType": "all",
    "destinationType": "instance",
    "protocol": "tcp",
    "portRange": "22",
    "enabled": True,
}

SAMPLE_SECURITY_GROUP = {
    "id": 12,
    "name": "web-servers",
    "description": "Web access",
    "rules": [SAMPLE_RULE],
    "active": True,
}


@pytest.fixture
def resource(mock_http: MagicMock) -> SecurityGroupsResource:
    """Return a security groups resource backed by a mocked HTTP client."""
    return SecurityGroupsResource(mock_http)


class TestSecurityGroupPayloadModels:
    """Tests for security group payload builders."""

    @pytest.mark.parametrize(
        ("path", "expected"),
        [
            ("securityGroup.name", "web-servers"),
            ("securityGroup.description", "Web access"),
        ],
    )
    def test_create_payload_field(self, path: str, expected: Any) -> None:
        """Build security group create payload fields."""
        payload = SecurityGroupCreate(name="web-servers", description="Web access").to_api_payload()

        assert nested_value(payload, path) == expected

    @pytest.mark.parametrize(
        ("path", "expected"),
        [
            ("securityGroup.name", "web-renamed"),
            ("securityGroup.description", "Updated"),
        ],
    )
    def test_update_payload_field(self, path: str, expected: Any) -> None:
        """Build security group update payload fields."""
        payload = SecurityGroupUpdate(name="web-renamed", description="Updated").to_api_payload()

        assert nested_value(payload, path) == expected

    @pytest.mark.parametrize(
        ("path", "expected"),
        [
            ("rule.ruleType", "customRule"),
            ("rule.name", "allow-ssh"),
            ("rule.direction", "ingress"),
            ("rule.policy", "accept"),
            ("rule.sourceType", "all"),
            ("rule.destinationType", "instance"),
            ("rule.protocol", "tcp"),
            ("rule.portRange", "22"),
        ],
    )
    def test_rule_create_payload_field(self, path: str, expected: Any) -> None:
        """Build security group rule create payload fields."""
        payload = SecurityGroupRuleCreate(
            name="allow-ssh",
            protocol="tcp",
            port_range="22",
        ).to_api_payload()

        assert nested_value(payload, path) == expected

    @pytest.mark.parametrize(
        ("path", "expected"),
        [
            ("rule.name", "allow-http"),
            ("rule.protocol", "tcp"),
            ("rule.portRange", "80"),
        ],
    )
    def test_rule_update_payload_field(self, path: str, expected: Any) -> None:
        """Build security group rule update payload fields."""
        payload = SecurityGroupRuleUpdate(
            name="allow-http",
            protocol="tcp",
            port_range="80",
        ).to_api_payload()

        assert nested_value(payload, path) == expected


class TestSecurityGroupsResource:
    """Tests for SecurityGroupsResource."""

    @pytest.mark.parametrize(("field", "expected"), [("id", 12), ("name", "web-servers")])
    def test_list_security_group_field(
        self,
        resource: SecurityGroupsResource,
        mock_http: MagicMock,
        field: str,
        expected: Any,
    ) -> None:
        """Parse listed security group fields."""
        mock_http.get.return_value = {"securityGroups": [SAMPLE_SECURITY_GROUP]}

        assert getattr(resource.list()[0], field) == expected

    def test_list_name_filter(self, resource: SecurityGroupsResource, mock_http: MagicMock) -> None:
        """Send security group name filters as query parameters."""
        mock_http.get.return_value = {"securityGroups": [SAMPLE_SECURITY_GROUP]}

        resource.list(name="web-servers")

        assert mock_http.get.call_args.kwargs["params"]["name"] == "web-servers"

    def test_get_by_name_returns_match(
        self,
        resource: SecurityGroupsResource,
        mock_http: MagicMock,
    ) -> None:
        """Return the first security group matching a name."""
        mock_http.get.return_value = {"securityGroups": [SAMPLE_SECURITY_GROUP]}

        assert resource.get_by_name("web-servers").id == 12

    def test_get_by_name_raises_when_missing(
        self,
        resource: SecurityGroupsResource,
        mock_http: MagicMock,
    ) -> None:
        """Raise when a named security group cannot be found."""
        mock_http.get.return_value = {"securityGroups": []}

        with pytest.raises(NotFoundError):
            resource.get_by_name("missing")

    def test_create_security_group_request(
        self,
        resource: SecurityGroupsResource,
        mock_http: MagicMock,
    ) -> None:
        """Send expected security group create request."""
        mock_http.post.return_value = {"securityGroup": SAMPLE_SECURITY_GROUP}

        resource.create(name="web-servers", description="Web access")

        assert mock_http.post.call_args.kwargs["json"]["securityGroup"]["name"] == "web-servers"

    def test_update_security_group_request(
        self,
        resource: SecurityGroupsResource,
        mock_http: MagicMock,
    ) -> None:
        """Send expected security group update request."""
        mock_http.put.return_value = {"securityGroup": SAMPLE_SECURITY_GROUP}

        resource.update(12, name="web-renamed")

        mock_http.put.assert_called_with(
            "/security-groups/12",
            json={"securityGroup": {"name": "web-renamed"}},
        )

    def test_delete_security_group(
        self, resource: SecurityGroupsResource, mock_http: MagicMock
    ) -> None:
        """Delete a security group by ID."""
        mock_http.delete.return_value = {"success": True}

        assert resource.delete(12) is True
        mock_http.delete.assert_called_with("/security-groups/12", params=None)

    def test_list_rules(self, resource: SecurityGroupsResource, mock_http: MagicMock) -> None:
        """Return rules embedded in a security group."""
        mock_http.get.return_value = {"securityGroup": SAMPLE_SECURITY_GROUP}

        assert resource.list_rules(12)[0].id == 90

    def test_create_rule_request(
        self, resource: SecurityGroupsResource, mock_http: MagicMock
    ) -> None:
        """Send expected security group rule create request."""
        mock_http.post.return_value = {"rule": SAMPLE_RULE}

        resource.create_rule(12, name="allow-ssh", protocol="tcp", port_range="22")

        mock_http.post.assert_called_with(
            "/security-groups/12/rules",
            json=SecurityGroupRuleCreate(
                name="allow-ssh",
                protocol="tcp",
                port_range="22",
            ).to_api_payload(),
        )

    def test_update_rule_request(
        self, resource: SecurityGroupsResource, mock_http: MagicMock
    ) -> None:
        """Send expected security group rule update request."""
        mock_http.put.return_value = {"rule": SAMPLE_RULE}

        resource.update_rule(12, 90, name="allow-http", port_range="80")

        mock_http.put.assert_called_with(
            "/security-groups/12/rules/90",
            json=SecurityGroupRuleUpdate(name="allow-http", port_range="80").to_api_payload(),
        )

    def test_delete_rule(self, resource: SecurityGroupsResource, mock_http: MagicMock) -> None:
        """Delete a security group rule by ID."""
        mock_http.delete.return_value = {"success": True}

        assert resource.delete_rule(12, 90) is True
        mock_http.delete.assert_called_with("/security-groups/12/rules/90")
