from werkzeug.security import check_password_hash, generate_password_hash
from utils import OrmBase
from datetime import datetime, timezone
from pydantic import BaseModel
from typing import Optional
from sqlmodel import Field, SQLModel, Column, TEXT, Relationship, select
from sqlalchemy import event, select


class UserPublic(OrmBase):
    username: str
    avatar_url: Optional[str]
    public_title: Optional[str]


class UserResponse(OrmBase):
    username: str
    email: str
    public_title: Optional[str]
    avatar_url: Optional[str]
    birthdate: Optional[datetime]
    role_name: Optional[str]
    created_at: datetime


class UserResponseList(BaseModel):
    page: int
    pages: int
    users: list[UserResponse]


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(sa_column=Column(TEXT(64), nullable=True))
    email: str = Field(sa_column=Column(TEXT(128), nullable=False, unique=True))
    avatar_url: Optional[str] = None
    public_title: Optional[str] = Field(sa_column=Column(TEXT(128), nullable=True))
    password_hash: str = Field(nullable=False)
    birthdate: Optional[datetime]
    created_at: datetime = datetime.now(timezone.utc)

    role_id: int | None = Field(default=None, foreign_key=("role.id"))
    role: Optional["Role"] | None = Relationship(back_populates="user")

    posts: list["Post"] | None = Relationship(back_populates="author")

    @property
    def password(self):
        raise AttributeError("password is not readable")

    # user_answers = db.relationship("UserAnswer", back_populates="user")

    @password.setter
    def password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        return f"User {self.username}"


@event.listens_for(User, "before_insert")
def before_user_insert(mapper, connection, target):
    if target.role_id is None:
        from .role import Role

        role_id = connection.execute(
            select(Role.id).where(Role.name == "user")
        ).scalar_one()

        target.role_id = role_id


class TokenBlocklist(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    jti: str = Field(nullable=False, index=True)
    created_at: datetime = datetime.now(timezone.utc)
