from factory import db
from datetime import datetime, timezone
from pydantic import BaseModel
from utils import OrmBase
from typing import Optional
from models.user import UserPublic, User
from sqlmodel import Field, SQLModel, Relationship, JSON, Column


class ArgsAllModel(BaseModel):
    page: Optional[int] = 1
    limit: Optional[int] = 4
    search: Optional[str] = ""


class PostResponse(OrmBase):
    title: str
    excerpt: str
    slug: str
    cover_url: Optional[str] = None
    meta: Optional[dict] = None
    likes: Optional[int] = None
    content_md: str
    author: UserPublic
    created_at: datetime


class PostResponseMini(OrmBase):
    title: str
    likes: Optional[int] = None
    excerpt: str
    slug: str
    created_at: datetime
    author: UserPublic


class PostResponseList(BaseModel):
    page: int
    pages: int
    posts: list[PostResponseMini]


class PostModel(BaseModel):
    title: str
    excerpt: Optional[str] = None
    cover_url: Optional[str] = None
    meta: Optional[dict] = None
    content_md: str


class Post(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(nullable=False)
    likes: int = Field(default=0)
    slug: str = Field(nullable=False)
    excerpt: str = Field(nullable=False)
    cover_url: str = Field(nullable=False)
    meta: dict = Field(sa_column=Column(JSON, default={}))
    content_md: str = Field(nullable=False)
    created_at: datetime = datetime.now(timezone.utc)

    author_id: int | None = Field(default=None, foreign_key=("user.id"))
    author: User | None = Relationship(back_populates="posts")

    def __repr__(self) -> str:
        return f"Post {self.id} by {self.author.username}"

    def wrap_formdata(self):
        return "efef"
