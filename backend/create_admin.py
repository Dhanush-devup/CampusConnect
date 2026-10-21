"""
Controlled Administrative Account Creation CLI Script.
Allows system administrators to provision admin accounts securely without exposing
any public registration endpoints.

Usage:
    python create_admin.py --email admin@campusconnect.edu --password Admin@123 --name "Placement Admin"
"""
import argparse
import sys
from app.auth import hash_password
from app.config import get_settings
from app.database import SessionLocal, init_db
from app.models import User

settings = get_settings()


def create_or_update_admin(email: str, password: str, name: str):
    """Provisions an administrator account in the SQLite database."""
    init_db()
    session = SessionLocal()
    try:
        clean_email = email.lower().strip()
        existing = session.query(User).filter(User.email == clean_email).first()

        hashed_pwd = hash_password(password)

        if existing:
            print(f"[!] User with email '{clean_email}' already exists. Updating to active admin role.")
            existing.role = "admin"
            existing.account_status = "active"
            existing.name = name.strip()
            existing.password_hash = hashed_pwd
            session.commit()
            print(f"[OK] Administrator account '{clean_email}' updated successfully.")
        else:
            admin_user = User(
                name=name.strip(),
                email=clean_email,
                password_hash=hashed_pwd,
                role="admin",
                account_status="active",
                company_id=None,
            )
            session.add(admin_user)
            session.commit()
            print(f"[OK] Administrator account '{clean_email}' created successfully (ID: {admin_user.user_id}).")
    except Exception as exc:
        session.rollback()
        print(f"[X] Failed to create administrator account: {exc}", file=sys.stderr)
        sys.exit(1)
    finally:
        session.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a CampusConnect Administrator Account")
    parser.add_argument("--email", default=settings.INITIAL_ADMIN_EMAIL, help="Admin email address")
    parser.add_argument("--password", default=settings.INITIAL_ADMIN_PASSWORD, help="Admin password")
    parser.add_argument("--name", default=settings.INITIAL_ADMIN_NAME, help="Admin display name")

    args = parser.parse_args()
    create_or_update_admin(email=args.email, password=args.password, name=args.name)
