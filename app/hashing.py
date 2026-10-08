import bcrypt
import hashlib

def hash_password(password: str) -> str:
    # 1. Convert string password to bytes
    password_bytes = password.encode("utf-8")
    # 2. Generate a secure random salt (Default cost/work factor is 12)
    salt = bcrypt.gensalt()
    # 3. Hash the password
    hashed_password = bcrypt.hashpw(password_bytes, salt).decode("utf-8")
    return hashed_password

def hash_session_token(session_token: str) -> str:
    # Fast hash (sha256) for random session tokens; passwords use the slow bcrypt hash above
    return hashlib.sha256(session_token.encode("utf-8")).hexdigest()
