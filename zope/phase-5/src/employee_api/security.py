"""Zope Security (Users, Roles, Basic Auth) helpers for REST APIs.

Spring Security equivalent:
  - `acl_users`                     ≈ UserDetailsService / In-memory or DB users
  - Roles (`HRManager`, `Viewer`)   ≈ GrantedAuthority (`ROLE_HR_MANAGER`, `ROLE_VIEWER`)
  - `require_roles(user, ...)`      ≈ `@PreAuthorize("hasAnyRole('HR_MANAGER', 'MANAGER')")`
  - `getSecurityManager().getUser()`≈ `SecurityContextHolder.getContext().getAuthentication()`
"""

from AccessControl import getSecurityManager

DEMO_USERS = [
    # (username, password, roles)
    ("hr_manager", "hr123", ["HRManager", "Viewer"]),
    ("viewer", "viewer123", ["Viewer"]),
]


def ensure_demo_users(root):
    """Create demo Zope users and roles inside `root.acl_users` once on first boot.

    In production, users come from ZMI `acl_users`, LDAP, or a PAS (PluggableAuthService)
    JWT/Bearer plugin.
    """
    # Register custom roles on the Zope root if missing
    existing_roles = list(getattr(root, "__ac_roles__", ()))
    for role in ("HRManager", "Viewer"):
        if role not in existing_roles:
            existing_roles.append(role)
            root.__ac_roles__ = tuple(existing_roles)

    acl_users = root.acl_users
    existing_usernames = set(acl_users.getUserNames())
    for username, password, roles in DEMO_USERS:
        if username not in existing_usernames:
            acl_users._doAddUser(username, password, roles, [])


def get_current_user_info(context):
    """Return `(username, roles_list, is_anonymous)` from Zope's SecurityManager."""
    user = getSecurityManager().getUser()
    username = user.getUserName()
    is_anonymous = username == "Anonymous User"
    roles = list(user.getRolesInContext(context))
    return username, roles, is_anonymous


def has_any_role(user_roles, allowed_roles):
    """Check if the user has at least one required role (Manager always allowed)."""
    user_set = set(user_roles)
    if "Manager" in user_set:
        return True
    return bool(user_set.intersection(set(allowed_roles)))
