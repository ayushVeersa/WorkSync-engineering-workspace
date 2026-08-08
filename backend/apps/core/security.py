from fastapi import HTTPException, status, Depends
# from fastapi.security import OAuth2PasswordBearer
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError

from apps.services.jwt import decode_access_token
from apps.services.user_service import get_user_by_email
from apps.models.user import User
from apps.db.database import get_db

# oauth2 = OAuth2PasswordBearer(
#     tokenUrl = "/auth/login"
# )

security = HTTPBearer()

def get_current_user(
    # token: str = Depends(oauth2),
    credentials: HTTPAuthorizationCredentials  = Depends(security),
    db: Session = Depends(get_db)
):
    try:
        token = credentials.credentials
        payload = decode_access_token(token)

        email = payload.get("sub")
        if email is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )

    except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    user = get_user_by_email(email, db)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not active",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user
