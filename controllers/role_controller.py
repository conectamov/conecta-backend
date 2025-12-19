from flask import Blueprint, request
from flask_jwt_extended import jwt_required, current_user
from factory import api, db
from spectree import Response
from utils import DefaultResponse
from models.role import (
    Role,
    RoleResponse,
    RoleResponseList,
    RoleResponseMini,
)
from sqlalchemy import select
from models.user import User

role_blueprint = Blueprint("role-blueprint", __name__, url_prefix="/roles")


def to_bool(val):
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        return val.lower() in ["true", "1", "yes"]
    if val is None:
        return False
    return bool(val)


@role_blueprint.get("/")
@jwt_required()
@api.validate(
    tags=["roles"],
    resp=Response(
        HTTP_200=RoleResponseList,
        HTTP_400=DefaultResponse,
        HTTP_404=DefaultResponse,
        HTTP_403=DefaultResponse,
    ),
    security={"BearerAuth": []},
)
def get_all():
    """
    Get all roles
    """

    if not current_user.role.can_access_sensitive_information:
        return {"msg": "Not authorized"}, 403

    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 5, type=int)

    role_pagination = db.paginate(
        select(Role).order_by(Role.id.desc()),
        page=page,
        per_page=limit,
        error_out=False,
    )

    roles = [
        RoleResponseMini.model_validate(
            {
                "id": role.id,
                "name": role.name,
            }
        ).model_dump()
        for role in role_pagination.items
    ]

    return {
        "page": role_pagination.page,
        "pages": role_pagination.pages,
        "roles": roles,
    }


@role_blueprint.get("/<int:role_id>")
@api.validate(
    tags=["roles"],
    resp=Response(
        HTTP_200=RoleResponse,
        HTTP_400=DefaultResponse,
        HTTP_404=DefaultResponse,
        HTTP_403=DefaultResponse,
    ),
    security={"BearerAuth": []},
)
@jwt_required()
def get_role(role_id):
    """
    Get a specific role
    """

    if not current_user.role.can_access_sensitive_information:
        return {"msg": "Not authorized"}, 403

    role = db.session.get(Role, role_id)
    if role is None:
        return {"msg": f"Couldn't find role with id {role_id}"}, 404

    response = {
        "id": role.id,
        "name": role.name,
        "can_manage_users": True if role.can_manage_users else False,
        "can_manage_subscriptions": True if role.can_manage_subscriptions else False,
        "can_create_posts": True if role.can_create_posts else False,
        "can_manage_posts": True if role.can_manage_posts else False,
        "can_manage_roles": True if role.can_manage_roles else False,
        "can_access_sensitive_information": True
        if role.can_access_sensitive_information
        else False,
    }

    return response


@role_blueprint.get("/<string:role_name>")
@api.validate(
    tags=["roles"],
    resp=Response(
        HTTP_200=RoleResponse,
        HTTP_400=DefaultResponse,
        HTTP_404=DefaultResponse,
        HTTP_403=DefaultResponse,
    ),
    security={"BearerAuth": []},
)
@jwt_required()
def get_role_by_name(role_name):
    """
    Get a specific role by name
    """

    if not current_user.role.can_access_sensitive_information:
        return {"msg": "Not authorized"}, 403

    role = db.session.scalars(select(Role).filter_by(name=role_name)).first()

    if role is None:
        return {"msg": f"Couldn't find role with name {role_name}"}, 404

    response = {
        "id": role.id,
        "name": role.name,
        "can_manage_users": True if role.can_manage_users else False,
        "can_manage_subscriptions": True if role.can_manage_subscriptions else False,
        "can_create_posts": True if role.can_create_posts else False,
        "can_manage_posts": True if role.can_manage_posts else False,
        "can_manage_roles": True if role.can_manage_roles else False,
        "can_access_sensitive_information": True
        if role.can_access_sensitive_information
        else False,
    }

    return response


@role_blueprint.post("/")
@api.validate(
    tags=["roles"],
    json=Role,
    resp=Response(
        HTTP_200=DefaultResponse,
        HTTP_400=DefaultResponse,
        HTTP_404=DefaultResponse,
        HTTP_403=DefaultResponse,
    ),
    security={"BearerAuth": []},
)
@jwt_required()
def create_role():
    """
    Create a new role
    """

    if not current_user.role.can_manage_roles:
        return {"msg": "Not authorized!"}, 403

    data = request.json

    if "name" not in data or not data["name"]:
        return {"msg": "Role name is required."}, 400

    if db.session.scalars(select(Role).filter_by(name=data["name"])).first():
        return {"msg": f"The role name '{data['name']}' has already been taken."}, 400

    role = Role(
        name=data["name"],
        can_manage_users=to_bool(data.get("can_manage_users")),
        can_manage_subscriptions=to_bool(data.get("can_manage_subscriptions")),
        can_create_posts=to_bool(data.get("can_create_posts")),
        can_manage_posts=to_bool(data.get("can_manage_posts")),
        can_manage_roles=to_bool(data.get("can_manage_roles")),
        can_access_sensitive_information=to_bool(
            data.get("can_access_sensitive_information")
        ),
    )

    try:
        db.session.add(role)
        db.session.commit()
    except:
        db.session.rollback()
        return {"msg": "Something went wrong!"}, 400
    return {"msg": "Role created successfuly!"}


@role_blueprint.put("/<int:role_id>")
@api.validate(
    tags=["roles"],
    resp=Response(
        HTTP_200=DefaultResponse,
        HTTP_400=DefaultResponse,
        HTTP_404=DefaultResponse,
        HTTP_403=DefaultResponse,
    ),
    security={"BearerAuth": []},
)
@jwt_required()
def update_role(role_id):

    if not current_user.role.can_manage_roles:
        return {"msg": "Not authorized!"}, 403

    role = db.session.get(Role, role_id)
    if role is None:
        return {"msg": f"Couldn't find role with id {role_id}"}, 404

    data = request.json

    if "name" in data and data["name"] != role.name:
        if db.session.scalars(select(Role).filter_by(name=data["name"])).first():
            return {
                "msg": f"The role name '{data['name']}' has already been taken."
            }, 400
        role.name = data["name"]

    boolean_fields = [
        "can_manage_users",
        "can_manage_subscriptions",
        "can_create_posts",
        "can_manage_posts",
        "can_manage_roles",
        "can_access_sensitive_information",
    ]

    for field in boolean_fields:
        if field in data:
            setattr(role, field, to_bool(data[field]))

    try:
        db.session.commit()
    except:
        db.session.rollback()
        return {"msg": "Oops something went wrong"}, 400

    return {"msg": "Updated successfully!"}


@role_blueprint.delete("/<int:role_id>")
@api.validate(
    tags=["roles"],
    resp=Response(
        HTTP_200=DefaultResponse,
        HTTP_400=DefaultResponse,
        HTTP_404=DefaultResponse,
        HTTP_403=DefaultResponse,
    ),
    security={"BearerAuth": []},
)
@jwt_required()
def delete_role(role_id):

    if not current_user.role.can_manage_roles:
        return {"msg": "Not authorized"}, 403

    role = db.session.get(Role, role_id)
    if role is None:
        return {"msg": f"Couldn't find role with id {role_id}"}, 404

    if role.name == "user":
        return {"msg": "Cannot delete the default role."}, 400

    user_role = db.session.scalars(select(Role).filter_by(name="user")).first()

    if user_role is None:
        return {
            "msg": "No default role found to transfer users in the current role to. Create a role named 'user'."
        }, 400

    try:
        users_to_transfer = db.session.scalars(
            select(User).filter_by(role_id=role.id)
        ).all()
        for u in users_to_transfer:
            u.role = user_role

        db.session.delete(role)
        db.session.commit()
    except:
        db.session.rollback()
        return {"msg": "Oops something went wrong"}, 400

    return {"msg": "Role deleted successfuly!"}
