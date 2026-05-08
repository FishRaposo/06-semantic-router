"""Permission checking utilities."""

from pydantic import BaseModel, Field


class UserPermissions(BaseModel):
    """Resolved permissions for a user."""

    user_id: str = Field(..., description="Unique user identifier")
    permissions: list[str] = Field(default_factory=list, description="List of granted permissions")
    roles: list[str] = Field(default_factory=list, description="User roles")


ROLE_PERMISSION_MAP: dict[str, list[str]] = {
    "admin": [
        "billing.read", "billing.write", "finance.approve",
        "support.read", "support.write", "sales.read", "sales.write",
    ],
    "agent": ["billing.read", "support.read", "support.write", "sales.read", "sales.write"],
    "viewer": ["billing.read", "support.read", "sales.read"],
}


class PermissionChecker:
    """Resolves and checks user permissions against required access levels."""

    def check_permission(self, user_permissions: list[str], required: str) -> bool:
        """Check if a user has a specific permission.

        Args:
            user_permissions: List of permissions granted to the user.
            required: The permission to check for.

        Returns:
            True if the user has the required permission.
        """
        return required in user_permissions

    def get_user_permissions(self, user_id: str, roles: list[str]) -> UserPermissions:
        """Resolve permissions for a user based on their assigned roles.

        Args:
            user_id: The user's unique identifier.
            roles: List of role names assigned to the user.

        Returns:
            A UserPermissions object with all resolved permissions.
        """
        permissions: set[str] = set()
        for role in roles:
            permissions.update(ROLE_PERMISSION_MAP.get(role, []))

        return UserPermissions(user_id=user_id, permissions=list(permissions), roles=roles)
