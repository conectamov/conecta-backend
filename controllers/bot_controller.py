from flask import Blueprint, request
from flask_jwt_extended import jwt_required, current_user
from models.bot import UserAnswer

bot_blueprint = Blueprint("bot-blueprint", __name__, url_prefix="/bot")


# @api.validate(
#     tags=["bot"],
#     query=ArgsAllModel,
#     resp=Response(HTTP_200=PostResponseList, HTTP_404=DefaultResponse),
# )
@bot_blueprint.get("/")
def get_all():
    return {"success": True}


# @post_blueprint.get("/<string:slug>")
# @api.validate(
#     tags=["posts"], resp=Response(HTTP_200=PostResponse, HTTP_404=DefaultResponse)
# )
# def get_post(slug):
#     """
#     Get specific post by slug
#     """
#     stmt = select(Post).options(joinedload(Post.author)).filter_by(slug=slug)

#     post = db.session.scalars(stmt).first()

#     if post is None:
#         return {"msg": "Couldn't find this post"}, 404

#     response_data = PostResponse.model_validate(post).model_dump()

#     if post.author:
#         response_data["author"] = {
#             "id": post.author.id,
#             "username": post.author.username,
#             "avatar_url": post.author.avatar_url,
#             "public_title": post.author.public_title,
#         }

#     return response_data


# @post_blueprint.get("/<int:post_id>")
# @api.validate(
#     tags=["posts"], resp=Response(HTTP_200=PostResponse, HTTP_404=DefaultResponse)
# )
# def get_post_by_id(post_id):
#     """
#     Get specific post by post_id
#     """
#     post = db.session.get(Post, post_id)

#     if post is None:
#         return {"msg": f"Couldn't find post with id {post_id}"}, 404

#     response_data = PostResponse.model_validate(post).model_dump()

#     if post.author:
#         response_data["author"] = {
#             "id": post.author.id,
#             "username": post.author.username,
#             "avatar_url": post.author.avatar_url,
#             "public_title": post.author.public_title,
#         }

#     return response_data


# @post_blueprint.post("/")
# @api.validate(
#     tags=["posts"],
#     json=PostModel,
#     resp=Response(
#         HTTP_200=DefaultResponse, HTTP_400=DefaultResponse, HTTP_401=DefaultResponse
#     ),
#     security={"BearerAuth": []},
# )
# @jwt_required()
# def create_post():
#     """
#     Create one post
#     """
#     if not current_user.role.can_create_posts:
#         return {"msg": "Not authorized!"}, 403

#     data = request.json

#     base_slug = generate_slug(data["title"])

#     slug = base_slug
#     counter = 1
#     while True:
#         conflict = db.session.scalars(select(Post).filter_by(slug=slug)).first()

#         if not conflict:
#             break

#         slug = f"{base_slug}-{counter}"
#         counter += 1

#     post = Post(
#         title=data["title"],
#         content_md=data["content_md"],
#         excerpt=data.get("excerpt") or build_excerpt(data["content_md"]),
#         slug=slug,
#         meta=data.get("meta"),
#         cover_url=data.get("cover_url"),
#         author_id=current_user.id,
#     )

#     try:
#         db.session.add(post)
#         db.session.commit()

#         return {
#             "msg": "Post created successfully!",
#             "post": {"id": post.id, "slug": post.slug},
#         }
#     except Exception as e:
#         db.session.rollback()
#         return {"msg": f"Something went wrong: {str(e)}"}, 400


# @post_blueprint.put("/<int:post_id>")
# @api.validate(
#     tags=["posts"],
#     resp=Response(
#         HTTP_200=PostResponse,
#         HTTP_400=DefaultResponse,
#         HTTP_404=DefaultResponse,
#         HTTP_401=DefaultResponse,
#     ),
#     security={"BearerAuth": []},
# )
# @jwt_required()
# def update_post(post_id):
#     """
#     Update an existing post
#     """
#     post = db.session.get(Post, post_id)
#     if not post:
#         return {"msg": "Post not found."}, 404

#     if current_user.id != post.author_id and not current_user.role.can_manage_posts:
#         return {"msg": "Not authorized!"}, 403

#     data = request.json

#     if "title" in data and data["title"] != post.title:
#         post.title = data["title"]
#         if "slug" not in data:
#             base_slug = generate_slug(data["title"])

#             existing = db.session.scalars(
#                 select(Post).filter_by(slug=base_slug)
#             ).first()

#             if existing and existing.id != post.id:
#                 base_slug = f"{base_slug}-{int(datetime.now(timezone.utc).timestamp())}"

#             post.slug = base_slug

#     if "slug" in data and data["slug"] != post.slug:
#         candidate = generate_slug(data["slug"])
#         existing = db.session.scalars(select(Post).filter_by(slug=candidate)).first()

#         if existing and existing.id != post.id:
#             return {"msg": f"The slug '{candidate}' has already been taken."}, 400
#         post.slug = candidate

#     # Resto do código permanece similar...
#     if "excerpt" in data:
#         post.excerpt = data["excerpt"]

#     if "cover_url" in data:
#         post.cover_url = data["cover_url"]

#     if "meta" in data:
#         if not isinstance(data["meta"], dict):
#             return {"msg": "Invalid meta format. Must be an object/dict."}, 400
#         post.meta = data["meta"]

#     if "content_md" in data:
#         post.content_md = data["content_md"]

#     if "author_id" in data and data["author_id"] != post.author_id:
#         if not current_user.role.can_manage_posts:
#             return {"msg": "Only admins can change post authorship"}, 403

#         new_author = db.session.get(User, data["author_id"])
#         if not new_author:
#             return {"msg": f"Author with id {data['author_id']} not found."}, 400
#         post.author_id = data["author_id"]

#     try:
#         db.session.commit()

#         return PostResponse.model_validate(post).model_dump()
#     except Exception as e:
#         db.session.rollback()
#         return {"msg": f"Update failed: {str(e)}"}, 400


# @post_blueprint.delete("/<int:post_id>")
# @api.validate(
#     tags=["posts"],
#     resp=Response(
#         HTTP_200=DefaultResponse, HTTP_404=DefaultResponse, HTTP_401=DefaultResponse
#     ),
#     security={"BearerAuth": []},
# )
# @jwt_required()
# def delete_post(post_id):
#     """
#     Delete a post by its id
#     """
#     post = db.session.get(Post, post_id)

#     if post is None:
#         return {"msg": f"Couldn't find post with id {post_id}"}, 404

#     if current_user.id != post.author_id and not current_user.role.can_manage_posts:
#         return {"msg": "Not authorized!"}, 403

#     try:
#         db.session.delete(post)
#         db.session.commit()
#         return {"msg": "Post deleted successfully!"}
#     except Exception as e:
#         db.session.rollback()
#         return {"msg": f"Delete failed: {str(e)}"}, 400
