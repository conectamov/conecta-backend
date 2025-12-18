from factory import api, db
from flask import Blueprint, request
from models import User, UserModel, UserResponse, UserResponseList, UserPublic
from sqlalchemy import select
from datetime import datetime, timezone
from utils import DefaultResponse
from spectree import Response
from flask_jwt_extended import jwt_required, current_user
from models.role import Role

user_blueprint = Blueprint("user-blueprint", __name__, url_prefix="/user")


@user_blueprint.get("/<int:user_id>")
@api.validate(
    tags=["users"],
    resp=Response(HTTP_200=UserResponse, HTTP_400=DefaultResponse),
    security={"BearerAuth": []},
)
@jwt_required()
def get_user(user_id):
    """
    Get sensitive user information (permission required)
    """
    if current_user.id != user_id:
        if not current_user.role.can_access_sensitive_information:
            return {"msg": f"Not authorized!"}, 403

    user = db.session.get(User, user_id)
    if user == None:
        return {"msg": f"Couldn't find user with id {user_id}"}, 404

    user.role_name = user.role.name

    response = UserResponse.model_validate(user).model_dump()

    return response


@user_blueprint.get("/me")
@api.validate(
    tags=["users"],
    resp=Response(HTTP_200=UserResponse, HTTP_400=DefaultResponse),
    security={"BearerAuth": []},
)
@jwt_required()
def get_me():
    """
    Get information of current user
    """
    user = db.session.get(User, current_user.id)
    if user == None:
        return {"msg": f"Couldn't find user with id {current_user.id}"}, 404

    user.role_name = user.role.name

    response = UserResponse.model_validate(user).model_dump()

    return response


@user_blueprint.get("/p/<int:user_id>")
@api.validate(
    tags=["users"],
    resp=Response(HTTP_200=UserPublic, HTTP_400=DefaultResponse),
    security={"BearerAuth": []},
)
@jwt_required()
def get_public_user(user_id):
    """
    Get user public information
    """
    user = db.session.get(User, user_id)
    if user == None:
        return {"msg": f"Couldn't find user with id {user_id}"}, 404

    response = UserPublic.model_validate(user).model_dump()

    return response


@user_blueprint.get("/")
@api.validate(
    tags=["users"],
    resp=Response(
        HTTP_200=UserResponseList,
        HTTP_400=DefaultResponse,
        HTTP_500=DefaultResponse,
        HTTP_403=DefaultResponse,
    ),
    security={"BearerAuth": []},
)
@jwt_required()
def get_all():
    """
    Get all users (permission required)
    """

    if not current_user.role.can_access_sensitive_information:
        return {"msg": "Not authorized"}, 403

    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 10, type=int)

    user_pagination = db.paginate(
        select(User), page=page, per_page=limit, error_out=False
    )

    users = []
    for user in user_pagination.items:
        role_name = user.role.name if user.role else None
        users.append(
            UserResponse.model_validate(
                {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "birthdate": user.birthdate,
                    "public_title": user.public_title,
                    "avatar_url": user.avatar_url,
                    "role_name": role_name,
                    "created_at": user.created_at,
                }
            ).model_dump()
        )

    return {
        "page": user_pagination.page,
        "pages": user_pagination.pages,
        "users": [user for user in users],
    }


@user_blueprint.post("/")
@api.validate(
    tags=["users"],
    json=UserModel,
    resp=Response(
        HTTP_200=UserResponse, HTTP_400=DefaultResponse, HTTP_500=DefaultResponse
    ),
)
def create_user():
    """
    Create a new user
    """
    data = request.json

    conflict = db.session.scalars(
        select(User).filter(
            (User.username == data["username"]) | (User.email == data["email"])
        )
    ).first()

    if conflict:
        if conflict.username == data["username"]:
            return {
                "msg": f"The username {data['username']} has already been taken"
            }, 400
        if conflict.email == data["email"]:
            return {"msg": f"The email {data['email']} has already been taken"}, 400

    user = User(
        username=data["username"],
        email=data["email"],
        password=data["password"],
        avatar_url=data["avatar_url"],
        public_title="Usuário",
        birthdate=datetime.fromisoformat(data["birthdate"])
        if data.get("birthdate")
        else None,
    )

    try:
        db.session.add(user)
        db.session.commit()
    except:
        return {"msg": "Oops, something went wrong"}, 500
    user.role_name = user.role.name
    return UserResponse.model_validate(user).model_dump()


@user_blueprint.put("/<int:user_id>")
@api.validate(
    tags=["users"],
    resp=Response(
        HTTP_200=DefaultResponse,
        HTTP_400=DefaultResponse,
        HTTP_404=DefaultResponse,
        HTTP_403=DefaultResponse,
    ),
    security={"BearerAuth": []},
)
@jwt_required()
def update_user(user_id):
    if current_user.id != user_id:
        if not current_user.role.can_manage_users:
            return {"msg": f"Not authorized!"}, 403

    user = db.session.get(User, user_id)
    if user is None:
        return {"msg": f"Couldn't find user with id {user_id}"}, 404

    data = request.json
    if "username" in data and data["username"] is not user.username:
        if db.session.scalars(
            select(User).filter_by(username=data["username"])
        ).first():
            return {
                "msg": f"The username {data['username']} has already been taken."
            }, 400
        user.username = data["username"]

    if "email" in data and data["email"] is not user.email:
        if db.session.scalars(select(User).filter_by(email=data["email"])).first():
            return {"msg": f"The email {data['email']} has already been taken."}, 400
        user.email = data["email"]

    if "avatar_url" in data:
        user.avatar_url = data["avatar_url"]

    if "public_title" in data:
        if not current_user.role.can_manage_users:
            return {"msg": "Not authorized to change public_title."}, 403
        else:
            user.public_title = data["public_title"]

    if "birthdate" in data:
        try:
            user.birthdate = datetime.fromisoformat(data["birthdate"])
        except:
            return {"msg": "Invalid date format. Use YYYY-MM-DD"}, 400

    if "role" in data:
        if not (
            current_user.role.can_manage_users and current_user.role.can_manage_roles
        ):
            return {"msg": "Not authorized to change role."}, 403
        else:
            foundRole = db.session.scalars(
                select(Role).filter_by(name=data["role"])
            ).first()

            if not foundRole:
                return {"msg": f"Couldn't find role with name {data['role']}"}, 400

            user.role_id = foundRole.id

    if "password" in data:
        user.password = data["password"]

    try:
        db.session.commit()
    except:
        db.session.rollback()
        return {"msg": "Oops something went wrong"}, 400
    return {"msg": "Updated successfuly!"}


@user_blueprint.delete("/<int:user_id>")
@api.validate(
    tags=["users"],
    resp=Response(
        HTTP_200=DefaultResponse,
        HTTP_400=DefaultResponse,
        HTTP_404=DefaultResponse,
        HTTP_403=DefaultResponse,
    ),
    security={"BearerAuth": []},
)
@jwt_required()
def delete_user(user_id):
    if current_user.id != user_id:
        if not current_user.role.can_manage_users:
            return {"msg": f"Not authorized!"}, 403

    user = db.session.get(User, user_id)
    if user is None:
        return {"msg": f"Couldn't find user with id {user_id}"}, 404
    try:
        db.session.delete(user)
        db.session.commit()
    except:
        db.session.rollback()
        return {"msg": "Oops something went wrong"}, 400
    return {"msg": "User deleted successfuly!"}
