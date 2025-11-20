from flask import Blueprint, request
from flask_jwt_extended import jwt_required, current_user
from factory import api, db
from spectree import Response
from utils import DefaultResponse
from models.post import Post, PostModel, PostResponseList, PostResponse, PostResponseMini
from datetime import datetime, timezone
from sqlalchemy import select
from models.user import User

post_blueprint = Blueprint('post-blueprint', __name__, url_prefix="/posts")

#constroi resumo
def build_excerpt(content: str, limit: int = 250) -> str:
    excerpt = content[:limit]
    if len(content) > limit:
        excerpt = excerpt.rsplit(" ", 1)[0] + "..."
    return excerpt


@post_blueprint.get("/")
@api.validate(
    tags=["posts"],
)
def get_all():
    """
    Get all posts
    """
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 5, type=int)

    post_pagination = db.paginate(
        select(Post).order_by(Post.created_at.desc()),
        page=page,
        per_page=limit,
        error_out=False
    )

    posts = [PostResponseMini.model_validate({
        "id": post.id,
        "title": post.title,
        "excerpt": post.excerpt,
        "slug": post.slug
    }).model_dump() for post in post_pagination.items]
    
    return {
        'page': post_pagination.page,
        'pages': post_pagination.pages,
        'posts': posts
    }

@post_blueprint.get("/<string:slug>")
@api.validate(
    tags=["posts"],
    resp=Response(HTTP_200=PostResponse, HTTP_404=DefaultResponse)
)
def get_post(slug):
    """
    Get specific post by slug
    """
    post = db.session.scalars(
        select(Post).filter_by(slug=slug)
    ).first()

    if post is None:
        return {"msg": "Couldn't find this post"}, 404
    
    response = PostResponse.model_validate({
        "id": post.id,
        "title": post.title,
        "excerpt": post.excerpt,
        "slug": post.slug,
        "cover_url": post.cover_url,
        "meta": post.meta,
        "content_md": post.content_md,
        "author_id": post.author_id,
        "created_at": post.created_at
    }).model_dump()   
    
    return response

@post_blueprint.post("/")
@api.validate(
    tags=["posts"],
    json=PostModel,
    resp=Response(HTTP_200=DefaultResponse, HTTP_400=DefaultResponse, HTTP_401=DefaultResponse)
)
@jwt_required()
def create_post():
    """
    Create one post
    """
    if not current_user.role.can_create_posts:
        return {"msg": "Not authorized!"}, 401

    data = request.json

    conflict = db.session.scalars(
        select(Post).filter_by(title=data["title"])
    ).first()

    if conflict:
        return {"msg": f"A post with the exactly same title '{data['title']}' already exists."}, 400

    slug = (
        data["title"].strip().lower()
            .replace(" ", "-")
            .replace("/", "-")
    )

    post = Post(
        title = data["title"],
        content_md = data["content_md"],
        excerpt = data["excerpt"] if data.get("excerpt") else build_excerpt(data["content_md"]),
        slug = slug,
        meta = data["meta"],
        cover_url = data["cover_url"],
        author_id = current_user.id
    )

    try: 
        db.session.add(post)
        db.session.commit()
    except:
        return {"msg": "Something went wrong!"}, 400
    return {"msg": "Post created successfuly!"}

@post_blueprint.put("/<int:post_id>")
@api.validate(
    tags=["posts"],
    resp = Response(HTTP_200=DefaultResponse, HTTP_400=DefaultResponse, HTTP_404=DefaultResponse, HTTP_401=DefaultResponse)
)
@jwt_required()
def update_post(post_id):
    """
    Update an existing post
    """
    post = db.session.get(Post, post_id)
    if not post:
        return {"msg": "Post not found."}, 404

    if current_user.id != post.author_id:
        if not current_user.role.can_manage_posts:
            return {"msg": "Not authorized!"}, 401

    data = request.json

    if "title" in data and data["title"] != post.title:
        post.title = data["title"]
        if "slug" not in data:
            generated = (
                data["title"].strip().lower()
                .replace(" ", "-")
                .replace("/", "-")
            )
            existing = db.session.scalars(select(Post).filter_by(slug=generated)).first()
            if existing and existing.id != post.id:
                generated = f"{generated}-{int(datetime.now(timezone.utc).timestamp())}"
            post.slug = generated

    if "slug" in data and data["slug"] != post.slug:
        candidate = data["slug"].strip()
        existing = db.session.scalars(select(Post).filter_by(slug=candidate)).first()
        if existing and existing.id != post.id:
            return {"msg": f"The slug '{candidate}' has already been taken."}, 400
        post.slug = candidate

    if "excerpt" in data and data["excerpt"] != post.excerpt:
        post.excerpt = data["excerpt"]

    if "cover_url" in data and data["cover_url"] != post.cover_url:
        post.cover_url = data["cover_url"]

    if "meta" in data:
        if not isinstance(data["meta"], dict):
            return {"msg": "Invalid meta format. Must be an object/dict."}, 400
        post.meta = data["meta"]

    if "content_md" in data and data["content_md"] != post.content_md:
        post.content_md = data["content_md"]

    if "author_id" in data and data["author_id"] != post.author_id:
        new_author = db.session.scalars(select(User).filter_by(id=data["author_id"])).first()
        if not new_author:
            return {"msg": f"Author with id {data['author_id']} not found."}, 400
        post.author_id = data["author_id"]

    db.session.add(post)
    db.session.commit()

    resp = {
        "title": post.title,
        "excerpt": post.excerpt,
        "slug": post.slug,
        "cover_url": post.cover_url,
        "meta": post.meta or {},
        "content_md": post.content_md,
        "author_id": post.author_id,
        "created_at": post.created_at,
    }

    response = PostResponse.model_validate(resp).model_dump()
    return response

@post_blueprint.delete("/<int:post_id>")
@api.validate(
    tags=["posts"],
    resp = Response(HTTP_200=DefaultResponse, HTTP_404=DefaultResponse, HTTP_401=DefaultResponse)
)
@jwt_required()
def delete_post(post_id):
    post = db.session.get(Post, post_id)

    if post is None:
        return {"msg": f"Couldn't find post with id {post_id}"}, 404

    if current_user.id != post.author_id:
        if not current_user.role.can_manage_posts:
            return {"msg": "Not authorized!"}, 401
        
    try: 
        db.session.delete(post)
        db.session.commit()
    except: 
        db.session.rollback()
        return {"msg": "Oops, something went wrong"}, 400
    return {"msg": 'Post deleted successfuly!'}