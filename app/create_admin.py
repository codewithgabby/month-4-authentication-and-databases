# create_admin.py
"""
Dev helper: create an admin user if it doesn't exist.

Usage:
    python create_admin.py --email admin@example.com --password secret123 --full "Admin Name"

If the user already exists, the script will upgrade their role to "admin".
"""
import argparse
from app.database import SessionLocal
from app.models.user_model import User
from app.utils.hash import hash_password

def create_or_promote_admin(email: str, password: str, full_name: str | None):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if user:
            # Promote existing user to admin (update password if provided)
            print(f"[info] User exists: {email} (id={user.id}). Promoting to admin.")
            user.role = "admin"
            if password:
                user.hashed_password = hash_password(password)
            if full_name:
                user.full_name = full_name
            db.commit()
            print("[ok] Promoted existing user to admin.")
            return user
        else:
            # Create new admin user
            new_user = User(
                email=email,
                full_name=full_name,
                hashed_password=hash_password(password),
                role="admin",
                is_active=True
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            print(f"[ok] Created new admin user: {email} (id={new_user.id})")
            return new_user
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create or promote an admin user (dev only).")
    parser.add_argument("--email", required=True, help="Admin email (e.g. admin@example.com)")
    parser.add_argument("--password", required=True, help="Password for admin")
    parser.add_argument("--full", dest="full_name", default=None, help="Full name (optional)")
    args = parser.parse_args()

    user = create_or_promote_admin(args.email, args.password, args.full_name)
    print()
    print("Login example (OAuth form):")
    print(f"curl -X POST -F \"username={args.email}\" -F \"password={args.password}\" http://127.0.0.1:8000/auth/login")
    print()
    print("Or, if your login endpoint is /auth/token (OAuth2 tokenUrl), use that path instead.")
