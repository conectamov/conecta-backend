from pydantic import BaseModel
from utils import OrmBase
from typing import Optional
from sqlmodel import Field, SQLModel, Column, TEXT, Relationship, VARCHAR
from models.user import User


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


class Role(SQLModel, table=True):
    __tablename__ = "role"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(sa_column=Column(VARCHAR(64), nullable=False))
    can_manage_users: Optional[bool] = False
    can_manage_subscriptions: Optional[bool] = False
    can_create_posts: Optional[bool] = False
    can_manage_posts: Optional[bool] = False
    can_manage_roles: Optional[bool] = False
    can_access_sensitive_information: Optional[bool] = False

    user: list[User] = Relationship(back_populates="role")

    def __repr__(self) -> str:
        return f"Role {self.name}"
