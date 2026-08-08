import bcrypt


def hash_password(password: str) -> str:
    """
    hash password using bcrypt
    """

    encoded_psswd = password.encode("utf-8")
    salt = bcrypt.gensalt()

    hashed_psswd = bcrypt.hashpw(encoded_psswd, salt)
    return hashed_psswd.decode("utf-8")


def verify_password(password, hash_psswd: str) -> bool:
    """
    This function takes password and hashed password as input.

    Verifies both using brcypt and return a bool.
    """

    encoded_passwd = password.encode("utf-8")
    encoded_hash_passwd = hash_psswd.encode("utf-8")

    return bcrypt.checkpw(encoded_passwd, encoded_hash_passwd)
