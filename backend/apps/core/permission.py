from fastapi import Depends, HTTPException, status

from apps.schemas.role import Role
from apps.models.user import User
from apps.core.security import get_current_user
from apps.core.logging import get_logger

logger = get_logger(__name__)


def require_roles(*role: Role):
    """
    check permissions according to the role
    """

    role_set = set(role)

    def _require_roles(
            current_user: User = Depends(get_current_user
    )):

            if current_user.role is None or current_user.role not in role_set:
                logger.warning(
                    "Permission denied for user=%s role=%s, required roles=%s",
                    current_user.email,
                    current_user.role,
                    role_set,
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough Permissions"
                    )

            logger.debug(
                "Permission granted for user=%s role=%s",
                current_user.email,
                current_user.role,
            )
            return current_user

    return _require_roles
