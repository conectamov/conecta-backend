from factory import db
from sqlalchemy import select
from datetime import datetime, timezone
from werkzeug.security import check_password_hash, generate_password_hash
from pydantic import BaseModel
from typing import Optional
from utils import OrmBase

class UserModel(BaseModel):
    username: str
    email: str
    password: str
    avatar_url: Optional[str]
    birthdate: Optional[datetime]

class UserResponse(OrmBase):
    username: str
    email: str
    public_title: Optional[str]
    avatar_url: Optional[str]
    birthdate: Optional[datetime]
    role: Optional[str]
    created_at: datetime

class UserResponseList(BaseModel):
    page: int
    pages: int
    users: list[UserResponse]

class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    avatar_url = db.Column(db.UnicodeText, nullable=True)
    public_title = db.Column(db.String(128), nullable=True)
    password_hash = db.Column(db.Unicode(256), nullable=False)
    birthdate = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default = lambda: datetime.now(timezone.utc))

    @property 
    def password():
        raise AttributeError("password's not a readable attribute")
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        if not self.password_hash:
            return True
        return check_password_hash(self.password_hash, password)
    
    role_id = db.Column(db.Integer, db.ForeignKey("role.id"))

    role = db.relationship("Role", back_populates="user")
    posts = db.relationship("Post", back_populates="author")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.role:
            from .role import Role
            self.role = db.session.scalars(
                select(Role).filter_by(name="user")
            ).first()
    
    def __repr__(self) -> str:
        return f"User {self.username}"