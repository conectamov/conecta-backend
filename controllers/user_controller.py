from factory import api, db
from flask import Blueprint, request
from models import User, UserModel, UserResponse
from sqlalchemy import select
from datetime import datetime, timezone
from utils import DefaultResponse
from spectree import Response

user_blueprint = Blueprint('user-blueprint', __name__, url_prefix="/user")

@user_blueprint.get("/<int:user_id>")
@api.validate(
    tags=["users"],
    resp=Response(HTTP_200=DefaultResponse, HTTP_400=DefaultResponse)
)
def get_user(user_id):
    """
    Get a specific user
    """

    user = db.session.get(User, user_id)
    if user is None:
        return {"msg": f"Couldn't find user with id {user_id}"}

    response = UserResponse.model_validate(user).model_dump()

    return response


@user_blueprint.get("/")
@api.validate(
    tags=["users"],
    resp=Response(HTTP_200=DefaultResponse, HTTP_400=DefaultResponse, HTTP_500=DefaultResponse)
)
def get_all():
    """
    Get all usersgenerate_password_hash
    """

    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)

    user_pagination = db.paginate(
     
   select(User),
        page=page, 
        limit=limit,
        error_out=False
    )

    users = [UserResponse.model_validate(user).model_dump() for user in user_pagination.items]

    return {
        'page': user_pagination.page,
        'pages': user_pagination.pages, 
        'users': [user for user in users]
    }

@user_blueprint.post("/")
@api.validate(
    tags=["users"],
    json=UserModel,
    resp=Response(HTTP_200=DefaultResponse, HTTP_400=DefaultResponse, HTTP_500=DefaultResponse)
)
def create_user():
    """
    Create a new user
    """
    data = request.json

    conflict = db.session.scalars(
        select(User).filter(
            (User.username is data["username"] | User.email is data["email"])    
        )
    ).first()

    if conflict: 
        if conflict.username is data["username"]:
            return {"msg": f"The username {data["username"]} has already been taken"}, 400
        if conflict.email is data["email"]:
            return {"msg": f"The email {data["email"]} has already been taken"}, 400
        
    user = User(
        username = data["username"],
        email = data["email"],
        password = data["password"],
        birthdate = datetime.fromisoformat(data["birthdate"]) if data.get("birthdate") else None
    )

    try: 
        db.session.add(user)
        db.session.commit()
    except:
        return {"msg": "Oops, something went wrong"}, 500
    
    return {"User created successfuly!"}

@user_blueprint.put("/<int:user_id>")
@api.validate(
    tags=["users"],
    resp = Response(HTTP_200=DefaultResponse, HTTP_400=DefaultResponse, HTTP_404=DefaultResponse, HTTP_403=DefaultResponse)
)
def update_user(user_id):
    #if current_user.id != user_id:
     #   if not current_user.role.can_manage_users:
      #      return {"msg": f"Not authorized!"}, 403

    user = db.session.get(User, user_id)
    if user is None:
        return {"msg": f"Couldn't find user with id {user_id}"}, 404
    
    data = request.json
    if "username" in data and data["username"] is not user.username:
        if db.session.scalars(select(User).filter_by(username=data["username"])).first():
            return {"msg": f"The username {data["username"]} has already been taken."}, 400
        user.username = data["username"] 
    
    if "email" in data and data["email"] is not user.email:
        if db.session.scalars(select(User).filter_by(email=data["email"])).first():
            return {"msg": f"The email {data['email']} has already been taken."}, 400
        user.email = data["email"]
    
    if "birthdate" in data:
        try:
            user.birthdate = datetime.fromisoformat(data["birthdate"])
        except:
            return {"msg": "Invalid date format. Use YYYY-MM-DD"}, 400
    
    if "password" in data:
        user.password = data["password"]
        
    try:
        db.session.commit()
    except:
        db.session.rollback()
        return {"msg": "Something went wrong"}, 400
    return {"msg": "Updated successfuly!"}    

@user_blueprint.delete("/<int:user_id>")
@api.validate(
    tags=["users"],
    resp = Response(HTTP_200=DefaultResponse, HTTP_400=DefaultResponse, HTTP_404=DefaultResponse, HTTP_403=DefaultResponse)
)
def delete_user(user_id):
    #if current_user.id != user_id:
     #   if not current_user.role.can_manage_users:
      #      return {"msg": f"Not authorized!"}, 403

    user = db.session.get(User, user_id)
    if user is None:
        return {"msg": f"Couldn't find user with id {user_id}"}, 404
    try:
        db.session.delete(user)
        db.session.commit()
    except:
        db.session.rollback()
        return {"msg": "Something went wrong"}, 400
    return {"msg": "User deleted successfuly!"}    