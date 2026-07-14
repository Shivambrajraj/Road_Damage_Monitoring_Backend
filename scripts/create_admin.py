# scripts/create_admin.py
import sys
import os

# Append the root directory to the Python path so it can resolve the 'app' module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import SecurityManager

# Pull credentials securely from Environment Variables instead of hardcoding
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "shivambrajraj@gmail.com")
ADMIN_USERNAME = ADMIN_EMAIL
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")

# Strict enforcement to prevent blank password structural writes
if not ADMIN_PASSWORD:
    raise RuntimeError("ADMIN_PASSWORD environment variable is not set in the environment matrix!")


def create_superuser():
    db = SessionLocal()
    try:
        print("Checking for existing administrative profiles...")
        admin = db.query(User).filter(User.email == ADMIN_EMAIL).first()
        hashed_password = SecurityManager.hash_password(ADMIN_PASSWORD)

        if admin:
            print("Admin account already exists — syncing credentials/flags.")
            admin.username = ADMIN_USERNAME
            admin.hashed_password = hashed_password
            admin.is_active = True
            admin.is_admin = True
            admin.is_verified = True
            db.add(admin)
            db.commit()
            print("Successfully updated existing admin account.")
        else:
            print("Creating system superuser account...")
            admin = User(
                username=ADMIN_USERNAME,
                email=ADMIN_EMAIL,
                hashed_password=hashed_password,
                is_active=True,
                is_admin=True,
                is_verified=True,
            )
            db.add(admin)
            db.commit()
            print("Successfully created Superuser Profile!")

        print(f"Email/Username: {ADMIN_EMAIL}")
        print("Password: (successfully pulled securely from environment vars)")

    except Exception as e:
        db.rollback()
        print(f"Error seeding administrator: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    create_superuser()