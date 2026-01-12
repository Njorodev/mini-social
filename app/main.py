from fastapi import FastAPI
from app.routers import auth, posts, feed

app = FastAPI(title="Mini Social API")

app.include_router(auth.router)
app.include_router(posts.router)
app.include_router(feed.router)

