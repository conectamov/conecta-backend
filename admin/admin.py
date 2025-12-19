from flask_admin.contrib.sqla import ModelView


def start_admin_views(admin, db):
    from models.user import User, TokenBlocklist
    from models.bot import UserAnswer
    from models.role import Role
    from models.post import Post

    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(UserAnswer, db.session))
    admin.add_view(ModelView(Role, db.session))
    admin.add_view(ModelView(TokenBlocklist, db.session))
    admin.add_view(PostView(Post, db.session))


class PostView(ModelView):
    form_excluded_columns = ["meta"]
