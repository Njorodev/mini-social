from sqlalchemy import (
    Column, Integer, String, Text, ForeignKey,
    DateTime, Boolean, UniqueConstraint
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True)
    password_hash = Column(String)
    bio = Column(Text)
    avatar_url = Column(String)
    role = Column(String, default="user")
    created_at = Column(DateTime, default=datetime.utcnow)

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey("users.id"))
    title = Column(String)
    content = Column(Text)
    image_url = Column(String)
    visibility = Column(String, default="public")
    created_at = Column(DateTime, default=datetime.utcnow)

class Like(Base):
    __tablename__ = "likes"
    __table_args__ = (UniqueConstraint("post_id", "user_id"),)

    id = Column(Integer, primary_key=True)
    post_id = Column(ForeignKey("posts.id"))
    user_id = Column(ForeignKey("users.id"))

class Follow(Base):
    __tablename__ = "follows"
    __table_args__ = (UniqueConstraint("follower_id", "following_id"),)

    follower_id = Column(ForeignKey("users.id"), primary_key=True)
    following_id = Column(ForeignKey("users.id"), primary_key=True)

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey("users.id"))
    token_hash = Column(String)
    revoked = Column(Boolean, default=False)
    expires_at = Column(DateTime)
