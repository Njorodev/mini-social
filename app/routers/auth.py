from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import User, RefreshToken
from app.schemas.user import UserCreate, Token, UserOut
from app.core.security import hash_password, verify, create_token, get_current_user
from datetime import timedelta, datetime, timezone
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.user import UserLogin # Import your new schema

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserOut)
def register(data: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = User(
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login", response_model=Token)
def login(
    # Change 'data: UserLogin' to this:
    data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    # OAuth2PasswordRequestForm uses 'username', even if the user types an email
    user = db.query(User).filter(
        (User.username == data.username) | 
        (User.email == data.username)
    ).first()
    
    if not user or not verify(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access = create_token({"sub": str(user.id)}, timedelta(minutes=30))
    refresh = create_token({"sub": str(user.id)}, timedelta(days=7))
    
    return {"access_token": access, "refresh_token": refresh, "token_type": "bearer"}