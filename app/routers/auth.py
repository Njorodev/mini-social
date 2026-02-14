from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import User, RefreshToken
from app.schemas.user import UserCreate, Token, UserOut
from app.core.security import hash_password, verify, create_token, get_current_user
from datetime import timedelta, datetime, timezone
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.user import UserLogin

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserOut, status_code=201)
def register(data: UserCreate, db: Session = Depends(get_db)):
    # 1. Check if username or email already exists
    existing_user = db.query(User).filter(
        (User.username == data.username) | (User.email == data.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=400, 
            detail="Username or email already registered"
        )

    # 2. Create the new user with role support
    new_user = User(
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password),
        # If data.role is not provided, SQLAlchemy uses the "user" default
        role=data.role if hasattr(data, 'role') and data.role else "user"
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
    
@router.post("/login", response_model=Token)
def login(
    data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    # 1. Find the user
    user = db.query(User).filter(
        (User.username == data.username) | 
        (User.email == data.username)
    ).first()
    
    # 2. Verify password
    if not user or not verify(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # 3. Create tokens
    access = create_token({"sub": str(user.id)}, timedelta(minutes=30))
    refresh = create_token({"sub": str(user.id)}, timedelta(days=7))
    
    # 4. Save Refresh Token to Database
    db_refresh = RefreshToken(
        user_id=user.id, 
        token_hash=refresh, 
        expires_at=datetime.now(timezone.utc) + timedelta(days=7)
    )
    db.add(db_refresh)
    db.commit()
    
    # 5. Return response
    return {
        "access_token": access, 
        "refresh_token": refresh, 
        "token_type": "bearer"
    }

@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Who am I: No input needed. 
    FastAPI extracts the token from the header and finds the user in the DB.
    """
    return current_user

@router.post("/logout")
def logout(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """
    Logout: Instead of asking for a token, we find the latest 
    active refresh token in the DB belonging to the current user.
    """
    db_token = db.query(RefreshToken).filter(
        RefreshToken.user_id == current_user.id,
        RefreshToken.revoked_at == None
    ).order_by(RefreshToken.created_at.desc()).first()

    if db_token:
        db_token.revoked_at = datetime.now(timezone.utc)
        db.commit()
        return {"message": "Logged out and token revoked"}
    
    return {"message": "No active session found"}

@router.post("/refresh", response_model=Token)
def refresh_access_token(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Refresh: Uses the identity of the current user to find 
    their valid refresh token and issue a new access token.
    """
    db_token = db.query(RefreshToken).filter(
        RefreshToken.user_id == current_user.id,
        RefreshToken.revoked_at == None
    ).first()

    if not db_token or db_token.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Session expired")

    new_access = create_token({"sub": str(current_user.id)}, timedelta(minutes=30))
    
    return {
        "access_token": new_access,
        "refresh_token": db_token.token_hash, 
        "token_type": "bearer"
    }