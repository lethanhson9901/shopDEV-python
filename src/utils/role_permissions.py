from enum import Enum, auto

class Permission(Enum):
    """Defines various permissions within the application."""
    CREATE_ITEM = auto()
    EDIT_ITEM = auto()
    DELETE_ITEM = auto()
    VIEW_ITEM = auto()
    MANAGE_USERS = auto()  # Permission to add, remove, or modify user roles
    VIEW_AUDIT_LOGS = auto()  # Permission to view audit logs for security or operational purposes
    MODIFY_SETTINGS = auto()  # Permission to change application settings
    # Extend with additional permissions as needed

class Role(Enum):
    """Defines roles and their associated permissions."""
    SHOP_OWNER = {Permission.CREATE_ITEM, Permission.EDIT_ITEM, Permission.DELETE_ITEM, Permission.VIEW_ITEM}
    CUSTOMER = {Permission.VIEW_ITEM}
    ADMIN = {
        Permission.CREATE_ITEM, Permission.EDIT_ITEM, Permission.DELETE_ITEM, 
        Permission.VIEW_ITEM, Permission.MANAGE_USERS, Permission.VIEW_AUDIT_LOGS, 
        Permission.MODIFY_SETTINGS
    }
    # Add more roles with their respective permissions here

def check_permission(role: Role, permission: Permission) -> bool:
    """
    Checks if a given role has a specific permission.

    Args:
        role (Role): The role to check permissions for.
        permission (Permission): The specific permission to check.

    Returns:
        bool: True if the role has the permission, False otherwise.
    """
    return permission in role.value
