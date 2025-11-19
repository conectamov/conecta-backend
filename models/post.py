from factory import db
from datetime import datetime, timezone
from pydantic import BaseModel
from utils import OrmBase

class PostModel(BaseModel):
    title: str
    excerpt: str
    cover_url: str | None = None
    meta: dict = {}
    content_md: str
    author_id: int

class PostResponse(OrmBase):
    title: str
    excerpt: str
    slug: str
    cover_url: str | None = None
    meta: dict = {}
    content_md: str
    author_id: int
    created_at: datetime

class PostResposeList(BaseModel):
    page: int
    pages: int
    posts: list[PostResponse]     

class Post(db.Model):
    __tablename__ = "post"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Unicode(256), nullable=False)
    slug = db.Column(db.UnicodeText, nullable=False)
    excerpt = db.Column(db.UnicodeText, nullable=False)
    cover_url = db.Column(db.Unicode(1024))
    meta = db.Column(db.JSON, default={})
    content_md = db.Column(db.UnicodeText, nullable=False)
    created_at = db.Column(db.DateTime, default = lambda: datetime.now(timezone.utc))

    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    author = db.relationship("User", back_populates="posts")

    def __repr__(self) -> str:
        return f"Post {self.id} by {self.author.username}"