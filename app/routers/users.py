from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import User, Follow
from app.core.security import get_current_user, check_admin

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/admin/users", dependencies=[Depends(check_admin)])
def list_all_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@router.get("/{username}")
def get_profile(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/{username}/follow")
def follow_user(
    username: str, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    # 1. Find the target user
    target_user = db.query(User).filter(User.username == username).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 2. Prevent self-following
    if current_user.id == target_user.id:
        raise HTTPException(
            status_code=400, 
            detail="You cannot follow yourself"
        )
    
    # 3. Check if already following (Idempotency)
    follow_check = db.query(Follow).filter_by(
        follower_id=current_user.id, 
        following_id=target_user.id
    ).first()
    
    if follow_check:
        # We return a 200/Success message because the end state (following) is already true
        return {"message": f"You are already following {username}"}
    
    # 4. Create new follow record
    new_follow = Follow(follower_id=current_user.id, following_id=target_user.id)
    db.add(new_follow)
    db.commit()
    
    return {"message": f"Successfully followed {username}"}

@router.delete("/{username}/unfollow")
def unfollow_user(
    username: str, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    # 1. Find the target user
    target_user = db.query(User).filter(User.username == username).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 2. Check if the follow relationship exists
    follow_record = db.query(Follow).filter_by(
        follower_id=current_user.id, 
        following_id=target_user.id
    ).first()
    
    # Perform the counts here where 'db' is available
    follower_count = db.query(Follow).filter(Follow.following_id == User.id).count()
    following_count = db.query(Follow).filter(Follow.follower_id == User.id).count()

    # Add the counts to the user object temporarily so the schema can see them
    User.follower_count = follower_count
    User.following_count = following_count
    if not follow_record:
        raise HTTPException(
            status_code=400, 
            detail=f"You are not following {username}"
        )
    
    # 3. Remove the relationship
    db.delete(follow_record)
    db.commit()
    
    return {"message": f"Successfully unfollowed {username}"}