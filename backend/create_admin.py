"""
Run once to create an admin account.
Usage: python create_admin.py
"""
import sys
from database import SessionLocal
import models
import auth

email    = input("Email: ").strip()
username = input("Username: ").strip()
password = input("Password: ").strip()

if not email or not username or not password:
    print("All fields required.")
    sys.exit(1)

db = SessionLocal()

if db.query(models.User).filter(models.User.email == email).first():
    print("A user with that email already exists.")
    db.close()
    sys.exit(1)

user = models.User(
    email=email,
    username=username,
    password_hash=auth.hash_password(password),
    role="admin",
)
db.add(user)
db.commit()
db.refresh(user)
db.close()

print(f"\nAdmin account created: {username} ({email})")
