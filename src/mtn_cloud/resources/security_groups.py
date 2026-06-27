"""Resource manager for MTN Cloud security groups."""

from __future__ import annotations

from typing import Any, List, Literal

from mtn_cloud.exceptions import NotFoundError
from mtn_cloud.models.security_group import (
    SecurityGroup,
    SecurityGroupCreate,
    SecurityGroupRule,
    SecurityGroupRuleCreate,
    SecurityGroupRuleUpdate,
    SecurityGroupUpdate,
)
from mtn_cloud.resources.base import BaseResource


class SecurityGroupsResource(BaseResource[SecurityGroup]):
    """
    Manage security groups and their firewall rules.

    Security groups are the firewall layer for MTN Cloud instances. You must
    create and configure a security group in the console (or via this SDK)
    before attaching it to an instance during provisioning.

    Example:
        # Create a security group
        sg = cloud.security_groups.create(
            name="web-servers",
            description="HTTP, HTTPS, and SSH access",
        )

        # Add rules
        cloud.security_groups.create_rule(
            sg.id,
            name="allow-ssh",
            direction="ingress",
            protocol="tcp",
            port_range="22",
        )
        cloud.security_groups.create_rule(
            sg.id,
            name="allow-https",
            direction="ingress",
            protocol="tcp",
            port_range="443",
        )

        # List all security groups
        for sg in cloud.security_groups.list():
            print(f"{sg.name} ({len(sg.rules)} rules)")
    """

    _path = "/security-groups"
    _model = SecurityGroup
    _name = "security group"
    _list_key = "securityGroups"
    _item_key = "securityGroup"

    def list(
        self,
        max_results: int | None = None,
        offset: int = 0,
        sort: str | None = None,
        direction: str | None = None,
        phrase: str | None = None,
        name: str | None = None,
        **filters: Any,
    ) -> list[SecurityGroup]:
        """
        List security groups.

        Args:
            max_results: Maximum number of results
            offset: Pagination offset
            phrase: Search phrase
            name: Filter by name
            **filters: Additional filters

        Returns:
            List of security groups
        """
        if name:
            filters["name"] = name
        return super().list(
            max_results=max_results,
            offset=offset,
            sort=sort,
            direction=direction,
            phrase=phrase,
            **filters,
        )

    def get(self, security_group_id: int) -> SecurityGroup:
        """
        Get a security group by ID (includes all rules).

        Args:
            security_group_id: Security group ID

        Returns:
            Security group with its rules
        """
        return super().get(security_group_id)

    def get_by_name(self, name: str) -> SecurityGroup:
        """
        Get a security group by name.

        Args:
            name: Security group name

        Returns:
            Matching security group

        Raises:
            NotFoundError: If not found
        """
        groups = self.list(name=name, max_results=1)
        if not groups:
            raise NotFoundError(resource_type="SecurityGroup", resource_id=name)
        return groups[0]

    def create(
        self,
        name: str,
        *,
        description: str | None = None,
    ) -> SecurityGroup:
        """
        Create a security group.

        Args:
            name: Security group name
            description: Optional description

        Returns:
            Created security group
        """
        model = SecurityGroupCreate(name=name, description=description)
        return self._create(model.to_api_payload())

    def update(
        self,
        security_group_id: int,
        *,
        name: str | None = None,
        description: str | None = None,
    ) -> SecurityGroup:
        """
        Update a security group.

        Args:
            security_group_id: Security group ID
            name: New name
            description: New description

        Returns:
            Updated security group
        """
        model = SecurityGroupUpdate(name=name, description=description)
        return self._update(security_group_id, model.to_api_payload())

    def delete(self, security_group_id: int) -> bool:
        """
        Delete a security group.

        Args:
            security_group_id: Security group ID

        Returns:
            True if deleted
        """
        return self._delete(security_group_id)

    # Rule management

    def list_rules(self, security_group_id: int) -> List[SecurityGroupRule]:
        """
        List rules for a security group.

        Rules are embedded in the GET /security-groups/{id} response.

        Args:
            security_group_id: Security group ID

        Returns:
            List of rules
        """
        sg = self.get(security_group_id)
        return sg.rules

    def create_rule(
        self,
        security_group_id: int,
        *,
        name: str | None = None,
        direction: Literal["ingress", "egress"] = "ingress",
        policy: Literal["accept", "deny"] = "accept",
        protocol: Literal["tcp", "udp", "icmp", "any"] | None = None,
        port_range: str | None = None,
        destination_port_range: str | None = None,
        source_type: Literal["cidr", "group", "instance", "all"] = "all",
        source: str | None = None,
        destination_type: Literal["cidr", "group", "instance", "all"] = "instance",
        destination: str | None = None,
        ethertype: Literal["IPv4", "IPv6"] | None = None,
        priority: int | None = None,
        enabled: bool | None = None,
    ) -> SecurityGroupRule:
        """
        Add a firewall rule to a security group.

        Args:
            security_group_id: Security group ID
            name: Rule display name
            direction: Traffic direction (`ingress` or `egress`)
            policy: Action (`accept` or `deny`)
            protocol: IP protocol (`tcp`, `udp`, `icmp`, `any`)
            port_range: Source port or range (e.g. `"22"`, `"8000-9000"`)
            destination_port_range: Destination port or range
            source_type: Source type (`cidr`, `group`, `instance`, `all`)
            source: Source CIDR or reference (required when source_type is `cidr`)
            destination_type: Destination type (`cidr`, `group`, `instance`, `all`)
            destination: Destination CIDR or reference
            ethertype: IP version (`IPv4` or `IPv6`)
            priority: Rule priority (lower = higher priority)
            enabled: Whether rule is active

        Returns:
            Created security group rule

        Example:
            # Allow SSH from anywhere
            cloud.security_groups.create_rule(
                sg_id,
                name="allow-ssh",
                direction="ingress",
                protocol="tcp",
                port_range="22",
            )

            # Allow HTTPS from a specific CIDR
            cloud.security_groups.create_rule(
                sg_id,
                name="allow-https-corp",
                direction="ingress",
                protocol="tcp",
                port_range="443",
                source_type="cidr",
                source="10.0.0.0/8",
            )
        """
        model = SecurityGroupRuleCreate(
            name=name,
            direction=direction,
            policy=policy,
            protocol=protocol,
            port_range=port_range,
            destination_port_range=destination_port_range,
            source_type=source_type,
            source=source,
            destination_type=destination_type,
            destination=destination,
            ethertype=ethertype,
            priority=priority,
            enabled=enabled,
        )
        path = f"{self._path}/{security_group_id}/rules"
        response = self._http.post(path, json=model.to_api_payload())
        rule_data = response.get("rule", response)
        return SecurityGroupRule.model_validate(rule_data)

    def update_rule(
        self,
        security_group_id: int,
        rule_id: int,
        *,
        name: str | None = None,
        direction: Literal["ingress", "egress"] | None = None,
        policy: Literal["accept", "deny"] | None = None,
        protocol: Literal["tcp", "udp", "icmp", "any"] | None = None,
        port_range: str | None = None,
        destination_port_range: str | None = None,
        source_type: Literal["cidr", "group", "instance", "all"] | None = None,
        source: str | None = None,
        destination_type: Literal["cidr", "group", "instance", "all"] | None = None,
        destination: str | None = None,
        ethertype: Literal["IPv4", "IPv6"] | None = None,
        priority: int | None = None,
        enabled: bool | None = None,
    ) -> SecurityGroupRule:
        """
        Update an existing security group rule.

        Args:
            security_group_id: Security group ID
            rule_id: Rule ID to update
            name: New display name
            direction: Traffic direction
            policy: Action (`accept` or `deny`)
            protocol: IP protocol
            port_range: Source port or range
            destination_port_range: Destination port or range
            source_type: Source type
            source: Source CIDR or reference
            destination_type: Destination type
            destination: Destination CIDR or reference
            ethertype: IP version
            priority: Rule priority
            enabled: Whether rule is active

        Returns:
            Updated security group rule
        """
        model = SecurityGroupRuleUpdate(
            name=name,
            direction=direction,
            policy=policy,
            protocol=protocol,
            port_range=port_range,
            destination_port_range=destination_port_range,
            source_type=source_type,
            source=source,
            destination_type=destination_type,
            destination=destination,
            ethertype=ethertype,
            priority=priority,
            enabled=enabled,
        )
        path = f"{self._path}/{security_group_id}/rules/{rule_id}"
        response = self._http.put(path, json=model.to_api_payload())
        rule_data = response.get("rule", response)
        return SecurityGroupRule.model_validate(rule_data)

    def delete_rule(self, security_group_id: int, rule_id: int) -> bool:
        """
        Remove a rule from a security group.

        Args:
            security_group_id: Security group ID
            rule_id: Rule ID to delete

        Returns:
            True if deleted
        """
        path = f"{self._path}/{security_group_id}/rules/{rule_id}"
        self._http.delete(path)
        return True
