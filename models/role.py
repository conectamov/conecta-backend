from factory import db
from pydantic import BaseModel
from utils import OrmBase
from typing import Optional

class RoleModel(BaseModel):
    name: str
    can_manage_users: Optional[bool]
    can_manage_subscriptions: Optional[bool]
    can_create_posts: Optional[bool]
    can_manage_posts: Optional[bool]
    can_manage_roles: Optional[bool]
    can_access_sensitive_information: Optional[bool]

class RoleResponse(OrmBase):
    name: str
    can_manage_users: bool
    can_manage_subscriptions: bool
    can_create_posts: bool
    can_manage_posts: bool
    can_manage_roles: bool
    can_access_sensitive_information: bool

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