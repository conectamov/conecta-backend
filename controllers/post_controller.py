from flask import Blueprint, request
from flask_jwt_extended import jwt_required, current_user
from factory import api, db
from spectree import Response
from utils import DefaultResponse
from models.post import Post, PostModel, PostResponseList, PostResponse
from datetime import datetime, timezone
from sqlalchemy import select

post_blueprint = Blueprint('post_controller', __name__, url_prefix="/posts")

@post_blueprint.post("/")
@api.validate(
    tags=["post"],
    json=PostModel,
    resp=Response(HTTP_200=DefaultResponse, HTTP_400=DefaultResponse, HTTP_401=DefaultResponse)
)
@jwt_required()
def create_post():

    if not current_user.role.can_create_posts:
        return {"msg": "Not authorized!"}, 401

    data = request.json

    post = Post(
        title = data["title"],
        content = data["content"],
        author_id = current_user.id
    )

    try: 
        db.session.add(post)
        db.session.commit()
    except:
        return {"msg": "Something went wrong!"}, 400
    return {"msg": "Post created successfuly!"}

@post_blueprint.get("/")
@api.validate(
    tags=["post"],
)
def get_all():
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 5, type=int)

    post_pagination = db.paginate(
        select(Post).order_by(Post.created_at.desc()),
        page=page,
        per_page=limit,
        error_out=False
    )

    posts = [PostResponse.model_validate(post).model_dump() for post in post_pagination.items]
    return {
        'page': post_pagination.page,
        'pages': post_pagination.pages,
        'posts': posts
    }

@post_blueprint.get("/<int:user_id>")
@api.validate(
    tags=["post"],
    resp=Response(HTTP_200=PostResponseList, HTTP_400=DefaultResponse)
)
def get_user_post(user_id):
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)

    post_pagination = db.paginate(
        select(Post).filter_by(author_id=user_id),
        page=page,
        per_page=limit,
        error_out=False
    )

    posts = [post for post in post_pagination.items]
    return {
        'posts': posts
    }