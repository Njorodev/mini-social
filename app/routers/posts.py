from fastapi import APIRouter, UploadFile, File, Depends, Form, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc
from app.db.session import get_db
from app.db.models import Post, User
from app.core.security import get_current_user
import uuid, os, shutil

router = APIRouter(prefix="/posts", tags=["Posts"])

# CREATE POST
@router.post("/")
def create_post(
    title: str = Form(None),
    content: str = Form(...),
    # This allows selection in Swagger/Postman, but defaults to "public"
    visibility: str = Form("public"), 
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Validate visibility input
    allowed_visibilities = ["public", "followers", "private"]
    if visibility not in allowed_visibilities:
        raise HTTPException(status_code=400, detail=f"Visibility must be one of {allowed_visibilities}")

    img_url = None
    if image:
        os.makedirs("uploads", exist_ok=True)
        name = f"{uuid.uuid4()}_{image.filename}"
        path = os.path.join("uploads", name)
        with open(path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        img_url = path.replace("\\", "/") 

    # 2. Save to DB
    new_post = Post(
        title=title, 
        content=content, 
        image_url=img_url, 
        visibility=visibility, # The selected value is stored here
        user_id=current_user.id
    )
    
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

# LIST POSTS (With Search, Filter, Sort, Pagination)
@router.get("/")
def list_posts(
    page: int = Query(1, ge=1),
    limit: int = Query(20, le=100),
    username: str = None,
    q: str = None,
    sort: str = "created_at",
    db: Session = Depends(get_db)
):
    query = db.query(Post).filter(Post.visibility == "public")

    # Filter by User
    if username:
        user = db.query(User).filter(User.username == username).first()
        if user:
            query = query.filter(Post.user_id == user.id)

    # Search Content/Title
    if q:
        query = query.filter(or_(Post.content.icontains(q), Post.title.icontains(q)))

    # Sorting
    if sort == "created_at":
        query = query.order_by(desc(Post.created_at))
    # Note: likes_count requires a relationship or join (implemented later)

    skip = (page - 1) * limit
    return query.offset(skip).limit(limit).all()

# VIEW SINGLE POST
@router.get("/{post_id}")
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

# UPDATE POST (Owner Only)
@router.patch("/{post_id}")
def update_post(
    post_id: int, 
    content: str = Form(None),
    visibility: str = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to edit this post")
    
    if content: post.content = content
    if visibility: post.visibility = visibility
    
    db.commit()
    db.refresh(post)
    return post

# DELETE POST (Owner or Admin)
@router.delete("/{post_id}")
def delete_post(
    post_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Permission Check: Owner OR Admin
    if post.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to delete this post")
    
    db.delete(post)
    db.commit()
    return {"message": "Post deleted successfully"}