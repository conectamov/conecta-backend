from factory import db
from pydantic import BaseModel
from utils import OrmBase
from typing import Optional

class RoleModel(BaseModel):
    name: str
    can_manage_users: Optional[str]
    can_manage_subscriptions: Optional[str]
    can_create_posts: Optional[str]
    can_manage_posts: Optional[str]
    can_manage_roles: Optional[str]
    can_access_sensitive_information: Optional[str]

class RoleResponse(OrmBase):
    name: str
    can_manage_users: str
    can_manage_subscriptions: str
    can_create_posts: str
    can_manage_posts: str
    can_manage_roles: str
    can_access_sensitive_information: str

class RoleResponseMini(OrmBase): 
    name: str

class RoleResponseList(BaseModel):
    page: int
    pages: int
    roles: list[RoleResponseMini]

class Role(db.Model):
    __tablename__ = "role"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    can_manage_users = db.Column(db.Boolean, default=False)
    can_manage_subscriptions = db.Column(db.Boolean, default=False)
    can_create_posts = db.Column(db.Boolean, default=False)
    can_manage_posts = db.Column(db.Boolean, default=False)
    can_manage_roles = db.Column(db.Boolean, default=False)
    can_access_sensitive_information = db.Column(db.Boolean, default=False)

    user = db.relationship("User", back_populates="role")

    def __repr__(self) -> str:
        return f"Role {self.name}"