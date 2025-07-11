from passlib.context import CryptContext

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Hash a plain-text password using bcrypt.
    """
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    """
    Verify a plain-text password against a hashed one.
    """
    return pwd_context.verify(plain, hashed)
