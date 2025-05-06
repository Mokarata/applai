# app/core/security.py
from passlib.context import CryptContext

# Configure the password hashing context
# Using bcrypt, which is a strong and widely recommended algorithm
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against a stored hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generates a hash for a plain password."""
    return pwd_context.hash(password)
