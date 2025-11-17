from factory import db
from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel
from utils import OrmBase

class Subscriber(db.Model):
    __tablename__ = "subscriber"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(256), unique=True, nullable=False)  