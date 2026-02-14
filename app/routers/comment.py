from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import Comment, Post, User
from app.core.security import get_current_user
from pydantic import BaseModel

router = APIRouter(tags=["Comments"])

class CommentCreate(BaseModel):
    content: str

#  POST /posts/{post_id}/comments
@router.post("/posts/{post_id}/comments")
def create_comment(
    post_id: int, 
    data: CommentCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    # Verify post exists
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    new_comment = Comment(
        content=data.content,
        post_id=post_id,
        user_id=current_user.id
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment


@router.get("/posts/{post_id}/comments")
def get_comments(
    post_id: int, 
    page: int = Query(1, ge=1), 
    limit: int = Query(10, le=50), 
    db: Session = Depends(get_db)
):
    # 1. First, check if the post actually exists
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Post not found"
        )

    # 2. Fetch comments
    skip = (page - 1) * limit
    comments = db.query(Comment).filter(Comment.post_id == post_id)\
                 .order_by(Comment.created_at.desc())\
                 .offset(skip).limit(limit).all()

    # 3. Handle empty comment list vs populated list
    if not comments:
        # return an empty list with a 200 OK because the post exists, 
        # it just doesn't have comments yet.
        return []

    return comments

# DELETE /comments/{comment_id}
@router.delete("/comments/{comment_id}")
def delete_comment(
    comment_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # Permission Check: Owner of comment OR Admin
    if comment.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")
    
    db.delete(comment)
    db.commit()
    return {"message": "Comment deleted"}