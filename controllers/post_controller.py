from flask import Blueprint, request
from flask_jwt_extended import jwt_required, current_user
from factory import api, db
from spectree import Response
from utils import DefaultResponse
from models.post import Post, PostModel, PostResponseList, PostResponse, PostResponseMini, ArgsAllModel
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from models.user import User, UserPublic
import re
import unicodedata

post_blueprint = Blueprint('post-blueprint', __name__, url_prefix="/posts")

def build_excerpt(content: str, limit: int = 250) -> str:
    excerpt = content[:limit]
    if len(content) > limit:
        excerpt = excerpt.rsplit(" ", 1)[0] + "..."
    return excerpt

def generate_slug(text: str) -> str:
    """Gera um slug mais robusto a partir do texto"""
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    
    slug = re.sub(r'[^\w\s-]', '', text.lower().strip())
    
    slug = re.sub(r'[-\s]+', '-', slug)
    
    return slug

@post_blueprint.get("/")
@api.validate(
    tags=["posts"],
    query=ArgsAllModel,
    resp=Response(HTTP_200=PostResponseList, HTTP_404=DefaultResponse)
)
def get_all():
    """
    Get all posts with authors by a search model
    """
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 5, type=int)
    search = request.args.get('search', "")

    stmt = (
        select(Post)
        .filter(
            (Post.title.ilike(f"%{search}%") | Post.content_md.ilike(f"{search}") 
             | Post.excerpt.ilike(f"{search}"))
        )
        .options(joinedload(Post.author))
        .order_by(Post.created_at.desc())
    )

    post_pagination = db.paginate(
        stmt,
        page=page,
        per_page=limit,
        error_out=False
    )

    posts = []
    for post in post_pagination.items:
        post_data = PostResponseMini.model_validate(post).model_dump()
        if post.author:
            post_data["author"] = {
                "id": post.author.id,
                "username": post.author.username,
                "avatar_url": post.author.avatar_url,
                "public_title": post.author.public_title
            }
        else:
            post_data["author"] = None
            
        posts.append(post_data)
    
    return {
        'page': post_pagination.page,
        'pages': post_pagination.pages,
        'total': post_pagination.total,
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
    stmt = (
        select(Post)
        .options(joinedload(Post.author))
        .filter_by(slug=slug)
    )
    
    post = db.session.scalars(stmt).first()

    if post is None:
        return {"msg": "Couldn't find this post"}, 404

    response_data = PostResponse.model_validate(post).model_dump()
    
    if post.author:
        response_data["author"] = {
            "id": post.author.id,
            "username": post.author.username,
            "avatar_url": post.author.avatar_url,
            "public_title": post.author.public_title
        }
    
    return response_data

@post_blueprint.post("/")
@api.validate(
    tags=["posts"],
    json=PostModel,
    resp=Response(HTTP_200=DefaultResponse, HTTP_400=DefaultResponse, HTTP_401=DefaultResponse),
    security={"BearerAuth": []}
)
@jwt_required()
def create_post():
    """
    Create one post 
    """
    if not current_user.role.can_create_posts: 
        return {"msg": "Not authorized!"}, 403

    data = request.json

    base_slug = generate_slug(data["title"])
    
    slug = base_slug
    counter = 1
    while True:
        conflict = db.session.scalars(
            select(Post).filter_by(slug=slug)
        ).first()
        
        if not conflict:
            break
            
        slug = f"{base_slug}-{counter}"
        counter += 1

    post = Post(
        title=data["title"],
        content_md=data["content_md"],
        excerpt=data.get("excerpt") or build_excerpt(data["content_md"]),
        slug=slug,
        meta=data.get("meta"),
        cover_url=data.get("cover_url"),
        author_id=current_user.id
    )

    try: 
        db.session.add(post)
        db.session.commit()
        
        return {
            "msg": "Post created successfully!",
            "post": {
                "id": post.id,
                "slug": post.slug
            }
        }
    except Exception as e:
        db.session.rollback()
        return {"msg": f"Something went wrong: {str(e)}"}, 400

@post_blueprint.put("/<int:post_id>")
@api.validate(
    tags=["posts"],
    resp=Response(HTTP_200=DefaultResponse, HTTP_400=DefaultResponse, HTTP_404=DefaultResponse, HTTP_401=DefaultResponse),
    security={"BearerAuth": []}
)
@jwt_required()
def update_post(post_id):
    """
    Update an existing post 
    """
    post = db.session.get(Post, post_id)
    if not post:
        return {"msg": "Post not found."}, 404

    if current_user.id != post.author_id and not current_user.role.can_manage_posts:
        return {"msg": "Not authorized!"}, 403  

    data = request.json

    if "title" in data and data["title"] != post.title:
        post.title = data["title"]
        if "slug" not in data:
            base_slug = generate_slug(data["title"])
            
            existing = db.session.scalars(
                select(Post).filter_by(slug=base_slug)
            ).first()
            
            if existing and existing.id != post.id:
                base_slug = f"{base_slug}-{int(datetime.now(timezone.utc).timestamp())}"
            
            post.slug = base_slug

    if "slug" in data and data["slug"] != post.slug:
        candidate = generate_slug(data["slug"]) 
        existing = db.session.scalars(
            select(Post).filter_by(slug=candidate)
        ).first()
        
        if existing and existing.id != post.id:
            return {"msg": f"The slug '{candidate}' has already been taken."}, 400
        post.slug = candidate

    # Resto do código permanece similar...
    if "excerpt" in data:
        post.excerpt = data["excerpt"]

    if "cover_url" in data:
        post.cover_url = data["cover_url"]

    if "meta" in data:
        if not isinstance(data["meta"], dict):
            return {"msg": "Invalid meta format. Must be an object/dict."}, 400
        post.meta = data["meta"]

    if "content_md" in data:
        post.content_md = data["content_md"]

    if "author_id" in data and data["author_id"] != post.author_id:
        if not current_user.role.can_manage_posts:
            return {"msg": "Only admins can change post authorship"}, 403
            
        new_author = db.session.get(User, data["author_id"])
        if not new_author:
            return {"msg": f"Author with id {data['author_id']} not found."}, 400
        post.author_id = data["author_id"]

    try:
        db.session.commit()
        
        return PostResponse.model_validate(post).model_dump()
    except Exception as e:
        db.session.rollback()
        return {"msg": f"Update failed: {str(e)}"}, 400

@post_blueprint.delete("/<int:post_id>")
@api.validate(
    tags=["posts"],
    resp=Response(HTTP_200=DefaultResponse, HTTP_404=DefaultResponse, HTTP_401=DefaultResponse),
    security={"BearerAuth": []}
)
@jwt_required()
def delete_post(post_id):
    """
    Delete a post by its id 
    """
    post = db.session.get(Post, post_id)

    if post is None:
        return {"msg": f"Couldn't find post with id {post_id}"}, 404

    if current_user.id != post.author_id and not current_user.role.can_manage_posts:
        return {"msg": "Not authorized!"}, 403  
        
    try: 
        db.session.delete(post)
        db.session.commit()
        return {"msg": 'Post deleted successfully!'}
    except Exception as e: 
        db.session.rollback()
        return {"msg": f"Delete failed: {str(e)}"}, 400