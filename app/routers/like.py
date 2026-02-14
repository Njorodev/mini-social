from app.db.models import Post, User, Like
from fastapi import APIRouter, Depends, HTTPException
from app.core.security import get_current_user
from app.db.session import get_db
from sqlalchemy.orm import Session
from app.db.models import Post, User

router = APIRouter(prefix="/like", tags=["Posts"])

#  POST /posts/{post_id}/like
@router.post("/{post_id}/like")
def like_post(
    post_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    # 1. Check if post exists
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # 2. Idempotency Check: Already liked?
    existing_like = db.query(Like).filter_by(
        user_id=current_user.id, 
        post_id=post_id
    ).first()
    
    if existing_like:
        return {"message": "Post already liked"}

    # 3. Create Like
    new_like = Like(user_id=current_user.id, post_id=post_id)
    db.add(new_like)
    db.commit()
    
    return {"message": "Post liked successfully"}

# DELETE /posts/{post_id}/like
@router.delete("/{post_id}/like")
def unlike_post(
    post_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    like_record = db.query(Like).filter_by(
        user_id=current_user.id, 
        post_id=post_id
    ).first()
    
    if not like_record:
        raise HTTPException(status_code=400, detail="You haven't liked this post")
    
    db.delete(like_record)
    db.commit()
    return {"message": "Post unliked successfully"}

#  GET /posts/{post_id}/likes (List users who liked)
@router.get("/{post_id}/likes")
def get_post_likes(post_id: int, db: Session = Depends(get_db)):
    # Join with User table to get the usernames of people who liked
    likes = db.query(User).join(Like).filter(Like.post_id == post_id).all()
    return likes