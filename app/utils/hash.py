from passlib.context import CryptContext
import hashlib

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def _normalize_password(password: str) -> str:
    """
    Ensures password is safe for bcrypt (<= 72 bytes)
    """
    if len(password.encode("utf-8")) > 72:
        # Pre-hash long passwords using SHA-256
        return hashlib.sha256(password.encode("utf-8")).hexdigest()
    return password

def hash_password(password: str) -> str:
    safe_password = _normalize_password(password)
    return pwd_context.hash(safe_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    safe_password = _normalize_password(plain_password)
    return pwd_context.verify(safe_password, hashed_password)