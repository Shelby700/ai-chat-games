from typing import Dict
from app.utils.security import hash_password, verify_password

class User:
    def __init__(self, username: str, password: str, role: str = "user"):
        self.username = username
        self.password_hash = hash_password(password)
        self.role = role

    def verify(self, password: str) -> bool:
        return verify_password(password, self.password_hash)

# In-memory user "database"
user_db: Dict[str, User] = {}

def register_user(username: str, password: str, role: str = "user") -> bool:
    if username in user_db:
        return False
    user_db[username] = User(username, password, role)
    return True

def authenticate_user(username: str, password: str) -> bool:
    user = user_db.get(username)
    if not user:
        return False
    return user.verify(password)

def get_user_role(username: str) -> str:
    user = user_db.get(username)
    return user.role if user else "user"
