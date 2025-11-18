from factory import db
from sqlalchemy import select
from datetime import datetime, timezone
from werkzeug.security import check_password_hash, generate_password_hash
from pydantic import BaseModel, Optional
from utils import OrmBase

class UserModel(BaseModel):
    username: str
    email: str
    password: str
    birthdate: Optional[datetime]

class UserResponse(OrmBase):
    username: str
    email: str
    birthdate: Optional[datetime]
    created_at: datetime


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
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
        if not self.passwrod_hash:
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