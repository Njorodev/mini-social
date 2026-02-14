from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import Post, Follow, User
from app.core.security import get_current_user
from sqlalchemy import or_
from typing import List

router = APIRouter(prefix="/feed", tags=["Feed"])

@router.get("/")
def get_personalized_feed(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    # 1. Get list of user IDs that current_user follows
    following_ids_tuples = db.query(Follow.following_id).filter(
        Follow.follower_id == current_user.id
    ).all()
    following_ids = [fid[0] for fid in following_ids_tuples]

    # 2. Build the query with visibility rules:
    # - Show MY posts (regardless of visibility)
    # - Show followed users' posts IF they are 'public' or 'followers'
    posts = db.query(Post).filter(
        or_(
            # Rule A: It's my own post
            Post.user_id == current_user.id,
            # Rule B: It's a post from someone I follow AND it's not private
            (Post.user_id.in_(following_ids)) & (Post.visibility.in_(["public", "followers"]))
        )
    ).order_by(Post.created_at.desc())

    # 3. Apply Pagination
    skip = (page - 1) * limit
    return posts.offset(skip).limit(limit).all()