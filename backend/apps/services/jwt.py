from datetime import timezone, datetime, timedelta
from jose import jwt

from apps.core.config import settings
from apps.core.logging import get_logger

logger = get_logger(__name__)


def create_access_token(data: dict):
    """
    This function creates access token while taking in the payload as arg.

    It creates token and set expiry as defined in the env.
    """
    payload = data.copy()

    expiry = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expiry)

    payload["exp"] = expiry

    token = jwt.encode(
            payload,
            settings.jwt_secret,
            algorithm=settings.algorithm
    )

    logger.info("Created access token for subject=%s", data.get("sub"))
    return token


def decode_access_token(access_token: str):
    """
    This function decodes token using jwt library from jose.

    It takes the access_token as the arg.
    """

    decoded = jwt.decode(
            access_token,
            settings.jwt_secret,
            algorithms=settings.algorithm
        )

    logger.info("Decoded access token for subject=%s", decoded.get("sub"))
    return decoded
