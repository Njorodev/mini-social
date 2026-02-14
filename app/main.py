from fastapi import FastAPI
from app.routers import auth, posts, feed, users, like, comment
from app.db.base import Base
from app.db.session import engine
import app.db.models

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Mini Social API")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(posts.router)
app.include_router(like.router)
app.include_router(comment.router)
app.include_router(feed.router)