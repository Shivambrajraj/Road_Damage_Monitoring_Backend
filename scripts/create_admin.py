# scripts/create_admin.py
import sys
import os

# Append the root directory to the Python path so it can resolve the 'app' module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import SecurityManager

def create_superuser():
    db = SessionLocal()
    try:
        print("Checking for existing administrative profiles...")
        admin_exists = db.query(User).filter(User.username == "admin").first()
        
        if admin_exists:
            print("Administration seed profile already configured.")
            return

        print("Creating system superuser account...")
        hashed_password = SecurityManager.hash_password("AdminSecure2026!")
        
        admin_user = User(
            username="admin",
            email="admin@cityinfrastructure.gov",
            hashed_password=hashed_password,
            is_active=True,
            is_admin=True  # Bypasses restricted route dependencies
        )
        
        db.add(admin_user)
        db.commit()
        print("Successfully created Superuser Profile!")
        print("Username: admin")
        print("Password: AdminSecure2026!")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding administrator: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_superuser()