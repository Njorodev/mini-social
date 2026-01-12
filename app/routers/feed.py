from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models import Post, Follow

router = APIRouter(prefix="/feed")

@router.get("/")
def feed(user_id: int, db: Session = Depends(SessionLocal)):
    following = db.query(Follow.following_id)\
                  .filter(Follow.follower_id == user_id)
    return db.query(Post)\
             .filter(Post.user_id.in_(following))\
             .order_by(Post.created_at.desc())\
             .all()
