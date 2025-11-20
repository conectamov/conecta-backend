from flask import Blueprint, request
from flask_jwt_extended import jwt_required, current_user
from factory import api, db
from spectree import Response
from utils import DefaultResponse
from models.role import Role, RoleResponse, RoleModel, RoleResponseList, RoleResponseMini
from datetime import datetime, timezone
from sqlalchemy import select
from models.user import User

role_blueprint = Blueprint('role-blueprint', __name__, url_prefix="/roles")

@role_blueprint.get("/")
@api.validate(
    tags=["roles"],
)
def get_all():
    """
    Get all roles
    """
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 5, type=int)

    role_pagination = db.paginate(
        select(Role).order_by(Role.created_at.desc()),
        page=page,
        per_page=limit,
        error_out=False
    )

    roles = [RoleResponseMini.model_validate({
        "id": role.id,
        "name": role.title,
    }).model_dump() for role in role_pagination.items]
    
    return {
        'page': role_pagination.page,
        'pages': role_pagination.pages,
        'posts': roles
    }

