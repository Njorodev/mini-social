from fastapi import APIRouter, UploadFile, File, Depends, Form
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import Post, User
from app.core.security import get_current_user
import uuid, os

router = APIRouter(prefix="/posts", tags=["Posts"])

@router.post("/")
def create_post(
    title: str = Form(...),
    content: str = Form(...),
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # Requirement: Auth required
):
    img_url = None
    if image:
        os.makedirs("uploads", exist_ok=True)
        name = f"{uuid.uuid4()}_{image.filename}"
        path = os.path.join("uploads", name)
        with open(path, "wb") as f:
            f.write(image.file.read())
        img_url = path

    post = Post(content=content, image_url=img_url, user_id=current_user.id)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post

@router.get("/")
def list_posts(page: int = 1, limit: int = 20, db: Session = Depends(get_db)):
    # Requirement: Pagination
    skip = (page - 1) * limit
    return db.query(Post).offset(skip).limit(limit).all()