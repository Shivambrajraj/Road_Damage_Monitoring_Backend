# app/core/security.py
import bcrypt

class SecurityManager:
    @staticmethod
    def hash_password(password: str) -> str:
        """Converts a clear text password into a secure cryptographic string."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Validates an incoming login password entry against the cached hash."""
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))