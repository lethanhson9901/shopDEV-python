# src/utils/role_permissions.py

from enum import Enum, auto

class Permission(Enum):
    """Defines various permissions within the application."""
    CREATE_ITEM = auto()
    EDIT_ITEM = auto()
    DELETE_ITEM = auto()
    VIEW_ITEM = auto()
    MANAGE_USERS = auto()
    VIEW_AUDIT_LOGS = auto()
    MODIFY_SETTINGS = auto()
    MANAGE_INVENTORY = auto()  # New permission for managing inventory details
    PROCESS_ORDERS = auto()  # New permission for processing customer orders
    ACCESS_REPORTS = auto()  # New permission for accessing various reports

class Role(Enum):
    """Defines roles and their associated permissions."""
    SHOP_OWNER = {Permission.CREATE_ITEM, Permission.EDIT_ITEM, Permission.DELETE_ITEM, Permission.VIEW_ITEM}
    CUSTOMER = {Permission.VIEW_ITEM}
    SHOP_MANAGER = {
        Permission.VIEW_ITEM, Permission.MANAGE_INVENTORY, Permission.PROCESS_ORDERS
    }  # New role
    ADMIN = {
        Permission.CREATE_ITEM, Permission.EDIT_ITEM, Permission.DELETE_ITEM, 
        Permission.VIEW_ITEM, Permission.MANAGE_USERS, Permission.VIEW_AUDIT_LOGS, 
        Permission.MODIFY_SETTINGS, Permission.MANAGE_INVENTORY, Permission.PROCESS_ORDERS,
        Permission.ACCESS_REPORTS
    }

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
