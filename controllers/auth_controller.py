from factory import api, db
from flask import Blueprint, request
from sqlalchemy import select
from models.user import User, TokenBlocklist
from pydantic import BaseModel
from flask_jwt_extended import create_access_token, jwt_required
from spectree import Response
from utils import DefaultResponse
from datetime import datetime, timezone, timedelta
from flask_jwt_extended import get_jwt


class LoginModel(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str


auth_blueprint = Blueprint("auth-blueprint", __name__, url_prefix="/auth")


@auth_blueprint.post("/login")
@api.validate(
    tags=["auth"],
    json=LoginModel,
    resp=Response(HTTP_200=LoginResponse, HTTP_401=DefaultResponse),
)
def login():
    data = request.json

    user = db.session.scalars(select(User).filter_by(email=data["email"])).first()

    if user and user.verify_password(data["password"]):
        return {"access_token": create_access_token(identity=user.username)}

    return {"msg": "Username and password do not match"}, 401


@auth_blueprint.post("/logout")
@api.validate(tags=["auth"], security={"BearerAuth": []})
@jwt_required()
def logout():
    """
    Logout user
    """
    jti = get_jwt()["jti"]
    now = datetime.now(timezone.utc)
    db.session.add(TokenBlocklist(jti=jti, created_at=now))
    db.session.commit()
    return {"success": True}
