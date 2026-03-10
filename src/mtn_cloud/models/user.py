"""
User Models
===========

Models for MTN Cloud users.
"""

from typing import Any, Optional
from pydantic import Field

from mtn_cloud.models.base import Resource


class UserRole(Resource):
    """User role."""

    authority: Optional[str] = Field(default=None, description="Role authority/code")
    description: Optional[str] = Field(default=None)
    role_type: Optional[str] = Field(default=None, alias="roleType")
    multitenant: bool = Field(default=False)
    multitenant_locked: bool = Field(default=False, alias="multitenantLocked")
    owner_id: Optional[int] = Field(default=None, alias="ownerId")


class User(Resource):
    """
    MTN Cloud user.

    Represents an authenticated user account.

    Example:
        ```python
        # Get current user
        user = cloud.whoami()
        print(f"Logged in as: {user.username}")
        print(f"Email: {user.email}")
        ```
    """

    # User details
    username: str = Field(..., description="Username")
    email: Optional[str] = Field(default=None, description="Email address")
    display_name: Optional[str] = Field(
        default=None,
        alias="displayName",
        description="Display name",
    )
    first_name: Optional[str] = Field(default=None, alias="firstName")
    last_name: Optional[str] = Field(default=None, alias="lastName")

    # Account
    account_id: Optional[int] = Field(default=None, alias="accountId")
    account: Optional[dict[str, Any]] = Field(default=None)

    # Role
    role: Optional[UserRole] = Field(default=None)
    roles: list[UserRole] = Field(default_factory=list)

    # Status
    enabled: bool = Field(default=True)
    account_expired: bool = Field(default=False, alias="accountExpired")
    account_locked: bool = Field(default=False, alias="accountLocked")
    password_expired: bool = Field(default=False, alias="passwordExpired")

    # Preferences
    linux_username: Optional[str] = Field(default=None, alias="linuxUsername")
    windows_username: Optional[str] = Field(default=None, alias="windowsUsername")

    # Default group
    default_group: Optional[dict[str, Any]] = Field(
        default=None,
        alias="defaultGroup"
    )
    default_cloud: Optional[dict[str, Any]] = Field(
        default=None,
        alias="defaultCloud"
    )

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

