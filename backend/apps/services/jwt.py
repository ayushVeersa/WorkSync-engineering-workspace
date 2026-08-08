from datetime import timezone, datetime, timedelta
from jose import jwt

from apps.core.config import settings


def create_access_token(data: dict):
    """
    This function creates access token while taking in the payload as arg.

    It creates token and set expiry as defined in the env.
    """
    payload = data.copy()

    expiry = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expiry)

    payload["exp"] = expiry

    return jwt.encode(
            payload,
            settings.jwt_secret,
            algorithm=settings.algorithm
    )


def decode_access_token(access_token: str):
    """
    This function decodes token using jwt library from jose.

    It takes the access_token as the arg.
    """
    
    return (
        jwt.decode(
            access_token,
            settings.jwt_secret,
            algorithms=settings.algorithm
        )
    )


