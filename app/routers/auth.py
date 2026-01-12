from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models import User
from app.core.security import hash_password, verify, create_token
from datetime import timedelta

router = APIRouter(prefix="/auth")

def db():
    d = SessionLocal()
    try: yield d
    finally: d.close()

@router.post("/register")
def register(data: dict, db: Session = Depends(db)):
    user = User(
        username=data["username"],
        email=data["email"],
        password_hash=hash_password(data["password"])
    )
    db.add(user)
    db.commit()
    return {"message": "registered"}

@router.post("/login")
def login(data: dict, db: Session = Depends(db)):
    user = db.query(User).filter(
        (User.username == data["username_or_email"]) |
        (User.email == data["username_or_email"])
    ).first()
    if not user or not verify(data["password"], user.password_hash):
        raise HTTPException(401)
    access = create_token({"sub": user.id}, timedelta(minutes=30))
    refresh = create_token({"sub": user.id}, timedelta(days=7))
    return {"access_token": access, "refresh_token": refresh}

