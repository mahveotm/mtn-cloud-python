"""Models for MTN Cloud users and roles."""

from typing import Any

from pydantic import Field

from mtn_cloud.models.base import Resource


class UserRole(Resource):
    """User role."""

    authority: str | None = Field(default=None, description="Role authority/code")
    description: str | None = Field(default=None)
    role_type: str | None = Field(default=None, alias="roleType")
    multitenant: bool = Field(default=False)
    multitenant_locked: bool = Field(default=False, alias="multitenantLocked")
    owner_id: int | None = Field(default=None, alias="ownerId")


class User(Resource):
    """
    MTN Cloud user.

    Represents an authenticated user account.

    Example:
        # Get current user
        user = cloud.whoami()
        print(f"Logged in as: {user.username}")
        print(f"Email: {user.email}")
    """

    username: str = Field(..., description="Username")
    email: str | None = Field(default=None, description="Email address")
    display_name: str | None = Field(
        default=None,
        alias="displayName",
        description="Display name",
    )
    first_name: str | None = Field(default=None, alias="firstName")
    last_name: str | None = Field(default=None, alias="lastName")

    account_id: int | None = Field(default=None, alias="accountId")
    account: dict[str, Any] | None = Field(default=None)

    role: UserRole | None = Field(default=None)
    roles: list[UserRole] = Field(default_factory=list)

    enabled: bool = Field(default=True)
    account_expired: bool = Field(default=False, alias="accountExpired")
    account_locked: bool = Field(default=False, alias="accountLocked")
    password_expired: bool = Field(default=False, alias="passwordExpired")

    linux_username: str | None = Field(default=None, alias="linuxUsername")
    windows_username: str | None = Field(default=None, alias="windowsUsername")

    default_group: dict[str, Any] | None = Field(default=None, alias="defaultGroup")
    default_cloud: dict[str, Any] | None = Field(default=None, alias="defaultCloud")

    @property
    def full_name(self) -> str:
        """Get full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.display_name or self.username

    @property
    def is_active(self) -> bool:
        """Check if user is active."""
        return self.enabled and not self.account_expired and not self.account_locked
