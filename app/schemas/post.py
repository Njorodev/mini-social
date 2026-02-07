class CommentBase(BaseModel):
    content: str

class CommentOut(CommentBase):
    id: int
    user_id: int
    post_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class PostBase(BaseModel):
    title: Optional[str] = None
    content: str
    visibility: str = "public"

class PostCreate(PostBase):
    pass # Image is handled via FastAPI Form/File data

class PostOut(PostBase):
    id: int
    image_url: Optional[str] = None
    user_id: int
    created_at: datetime
    updated_at: datetime
    likes_count: int = 0
    comments: List[CommentOut] = []

    model_config = ConfigDict(from_attributes=True)