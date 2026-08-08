import bcrypt

from apps.core.logging import get_logger

logger = get_logger(__name__)


def hash_password(password: str) -> str:
    """
    hash password using bcrypt
    """

    encoded_psswd = password.encode("utf-8")
    salt = bcrypt.gensalt()

    hashed_psswd = bcrypt.hashpw(encoded_psswd, salt)
    logger.info("Hashed a new password")
    return hashed_psswd.decode("utf-8")


def verify_password(password, hash_psswd: str) -> bool:
    """
    This function takes password and hashed password as input.

    Verifies both using brcypt and return a bool.
    """

    encoded_passwd = password.encode("utf-8")
    encoded_hash_passwd = hash_psswd.encode("utf-8")

    result = bcrypt.checkpw(encoded_passwd, encoded_hash_passwd)
    logger.debug("Password verification result: %s", result)
    return result
