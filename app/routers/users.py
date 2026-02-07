from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import User, Follow
from app.core.security import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/{username}")
def get_profile(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/{username}/follow")
def follow_user(username: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    target_user = db.query(User).filter(User.username == username).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    follow_check = db.query(Follow).filter_by(
        follower_id=current_user.id, 
        following_id=target_user.id
    ).first()
    
    if not follow_check:
        new_follow = Follow(follower_id=current_user.id, following_id=target_user.id)
        db.add(new_follow)
        db.commit()
    return {"message": f"You followed {username}"}