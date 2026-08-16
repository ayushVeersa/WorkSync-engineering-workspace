from fastapi import HTTPException, status, Depends, Request
from sqlalchemy.orm import Session
from jose import JWTError

from apps.services.jwt import decode_access_token
from apps.services.user_service import get_user_by_email
from apps.models.user import User
from apps.db.database import get_db
from apps.core.logging import get_logger

logger = get_logger(__name__)

ACCESS_TOKEN_COOKIE = "worksync_access_token"

def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        token = request.cookies.get(ACCESS_TOKEN_COOKIE)
        if not token:
            authorization = request.headers.get("Authorization", "")
            if authorization.lower().startswith("bearer "):
                token = authorization.split(" ", 1)[1].strip()

        if not token:
            logger.warning("Missing auth token in cookie or Authorization header")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

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
