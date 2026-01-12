from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from app.core.config import settings

pwd = CryptContext(schemes=["bcrypt"])

def hash_password(p): return pwd.hash(p)
def verify(p, h): return pwd.verify(p, h)

def create_token(data, exp):
    to_encode = data.copy()
    to_encode["exp"] = datetime.utcnow() + exp
    return jwt.encode(to_encode, settings.JWT_SECRET, "HS256")

