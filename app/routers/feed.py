from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import Post, Follow, User
from app.core.security import get_current_user
from typing import List

router = APIRouter(prefix="/feed", tags=["Feed"])

@router.get("/")
def get_personalized_feed(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user), # Ensures only logged-in users see feed
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    # Requirement: Get IDs of users current_user follows
    following_ids = db.query(Follow.following_id).filter(
        Follow.follower_id == current_user.id
    ).all()
    
    # Convert list of tuples to flat list and include current_user.id
    target_ids = [fid[0] for fid in following_ids] + [current_user.id]

    # Requirement: Returns posts from followed users + your own with pagination
    skip = (page - 1) * limit
    posts = db.query(Post).filter(Post.user_id.in_(target_ids))\
        .order_by(Post.created_at.desc())\
        .offset(skip).limit(limit).all()
        
    return posts