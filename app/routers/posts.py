from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models import Post, Like
import uuid, os

router = APIRouter(prefix="/posts")

@router.post("/")
def create_post(
    content: str,
    image: UploadFile = File(None),
    db: Session = Depends(SessionLocal)
):
    img_url = None
    if image:
        name = f"{uuid.uuid4()}_{image.filename}"
        path = f"uploads/{name}"
        with open(path, "wb") as f:
            f.write(image.file.read())
        img_url = path

    post = Post(content=content, image_url=img_url)
    db.add(post)
    db.commit()
    return post
