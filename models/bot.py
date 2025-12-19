from factory import db
from datetime import datetime, timezone
from pydantic import BaseModel
from utils import OrmBase
from typing import List, Optional
from sqlmodel import Field, SQLModel, ARRAY, Column, TEXT, Relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.dialects import postgresql


class UserAnswer(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    answers: Optional[List[int]] = Field(default=None, sa_column=Column(ARRAY(TEXT)))


# TODO: questions model
