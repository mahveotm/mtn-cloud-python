"""Models and payload builders for MTN Cloud security groups."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import Field

from mtn_cloud.models.base import BaseModel, Resource


class SecurityGroupRule(BaseModel):
    """A single firewall rule within a security group."""

    id: int
    name: str | None = None
    rule_type: str | None = Field(default=None, alias="ruleType")
    custom_rule: bool | None = Field(default=None, alias="customRule")
    direction: Literal["ingress", "egress"] | None = None
    policy: Literal["accept", "deny"] | None = None
    source_type: str | None = Field(default=None, alias="sourceType")
    source: str | None = None
    port_range: str | None = Field(default=None, alias="portRange")
    destination_port_range: str | None = Field(default=None, alias="destinationPortRange")
    destination_type: str | None = Field(default=None, alias="destinationType")
    destination: str | None = None
    protocol: str | None = None
    ethertype: str | None = None
    priority: int | None = None
    enabled: bool | None = None

    def __str__(self) -> str:
        return (
            f"SecurityGroupRule(id={self.id}, direction={self.direction}, "
            f"protocol={self.protocol}, port={self.port_range})"
        )

    def __repr__(self) -> str:
        return str(self)


class SecurityGroup(Resource):
    """
    MTN Cloud security group.

    Security groups act as the firewall layer for instances. Rules control
    which traffic is allowed in (ingress) and out (egress).

    Example:
        sg = cloud.security_groups.create(
            name="web-servers",
            description="Allow HTTP/HTTPS/SSH",
        )
        cloud.security_groups.create_rule(
            sg.id,
            name="allow-ssh",
            direction="ingress",
            protocol="tcp",
            port_range="22",
        )
    """

    description: str | None = None
    rules: list[SecurityGroupRule] = Field(default_factory=list)
    active: bool | None = None
    enabled: bool | None = None
    external_id: str | None = Field(default=None, alias="externalId")
    zone: dict[str, Any] | None = None
    tenant: dict[str, Any] | None = None


class SecurityGroupCreate(BaseModel):
    """Payload builder for creating a security group."""

    name: str
    description: str | None = None

    def to_api_payload(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"name": self.name}
        if self.description is not None:
            payload["description"] = self.description
        return {"securityGroup": payload}


class SecurityGroupUpdate(BaseModel):
    """Payload builder for updating a security group."""

    name: str | None = None
    description: str | None = None

    def to_api_payload(self) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        if self.name is not None:
            payload["name"] = self.name
        if self.description is not None:
            payload["description"] = self.description
        return {"securityGroup": payload}


class SecurityGroupRuleCreate(BaseModel):
    """
    Payload builder for creating a security group rule.

    Confirmed fields from live API inspection.
    """

    name: str | None = None
    direction: Literal["ingress", "egress"] = "ingress"
    policy: Literal["accept", "deny"] = "accept"
    protocol: Literal["tcp", "udp", "icmp", "any"] | None = None
    port_range: str | None = None
    destination_port_range: str | None = None
    source_type: Literal["cidr", "group", "instance", "all"] = "all"
    source: str | None = None
    destination_type: Literal["cidr", "group", "instance", "all"] = "instance"
    destination: str | None = None
    ethertype: Literal["IPv4", "IPv6"] | None = None
    priority: int | None = None
    enabled: bool | None = None

    def to_api_payload(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "ruleType": "customRule",
            "direction": self.direction,
            "policy": self.policy,
            "sourceType": self.source_type,
            "destinationType": self.destination_type,
        }
        if self.name is not None:
            payload["name"] = self.name
        if self.protocol is not None:
            payload["protocol"] = self.protocol
        if self.port_range is not None:
            payload["portRange"] = self.port_range
        if self.destination_port_range is not None:
            payload["destinationPortRange"] = self.destination_port_range
        if self.source is not None:
            payload["source"] = self.source
        if self.destination is not None:
            payload["destination"] = self.destination
        if self.ethertype is not None:
            payload["ethertype"] = self.ethertype
        if self.priority is not None:
            payload["priority"] = self.priority
        if self.enabled is not None:
            payload["enabled"] = self.enabled
        return {"rule": payload}


class SecurityGroupRuleUpdate(BaseModel):
    """Payload builder for updating an existing security group rule."""

    name: str | None = None
    direction: Literal["ingress", "egress"] | None = None
    policy: Literal["accept", "deny"] | None = None
    protocol: Literal["tcp", "udp", "icmp", "any"] | None = None
    port_range: str | None = None
    destination_port_range: str | None = None
    source_type: Literal["cidr", "group", "instance", "all"] | None = None
    source: str | None = None
    destination_type: Literal["cidr", "group", "instance", "all"] | None = None
    destination: str | None = None
    ethertype: Literal["IPv4", "IPv6"] | None = None
    priority: int | None = None
    enabled: bool | None = None

    def to_api_payload(self) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        if self.name is not None:
            payload["name"] = self.name
        if self.direction is not None:
            payload["direction"] = self.direction
        if self.policy is not None:
            payload["policy"] = self.policy
        if self.protocol is not None:
            payload["protocol"] = self.protocol
        if self.port_range is not None:
            payload["portRange"] = self.port_range
        if self.destination_port_range is not None:
            payload["destinationPortRange"] = self.destination_port_range
        if self.source_type is not None:
            payload["sourceType"] = self.source_type
        if self.source is not None:
            payload["source"] = self.source
        if self.destination_type is not None:
            payload["destinationType"] = self.destination_type
        if self.destination is not None:
            payload["destination"] = self.destination
        if self.ethertype is not None:
            payload["ethertype"] = self.ethertype
        if self.priority is not None:
            payload["priority"] = self.priority
        if self.enabled is not None:
            payload["enabled"] = self.enabled
        return {"rule": payload}
