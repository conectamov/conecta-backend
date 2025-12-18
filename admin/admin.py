from flask_admin.contrib.sqla import ModelView


def start_admin_views(admin, db):
    from models import User, Post

    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(Post, db.session))
