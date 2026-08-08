from fastapi import HTTPException, status, Depends
# from fastapi.security import OAuth2PasswordBearer
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError

from apps.services.jwt import decode_access_token
from apps.services.user_service import get_user_by_email
from apps.models.user import User
from apps.db.database import get_db
from apps.core.logging import get_logger

logger = get_logger(__name__)

# oauth2 = OAuth2PasswordBearer(
#     tokenUrl = "/auth/login"
# )

security = HTTPBearer()

def get_current_user(
    # token: str = Depends(oauth2),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    try:
        token = credentials.credentials
        payload = decode_access_token(token)

        email = payload.get("sub")
        if email is None:
                logger.warning("Token payload missing 'sub' claim")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )

    except JWTError:
            logger.warning("JWT validation failed for token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    user = get_user_by_email(email, db)

    if user is None:
        logger.warning("Authenticated token references unknown email: %s", email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        logger.warning("Authenticated user is inactive: %s", email)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not active",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.info("Authenticated user=%s id=%s role=%s", user.email, user.id, user.role)
    return user
