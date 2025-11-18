# Seed Default Roles
import os
from factory import db, create_app
from models.role import Role
from dotenv import load_dotenv
from sqlalchemy import select
from models.user import User
from models.post import Post
from datetime import datetime, timezone

load_dotenv()

app = create_app()

with app.app_context():
    if db.session.query(Role).count() == 0:
        role = Role(name = "user")
        db.session.add(role)
        role = Role(
            name = "admin",
            can_manage_users = True,
            can_manage_subscriptions = True,
            can_create_posts = True,
            can_manage_posts = True,
            can_manage_roles = True,
            can_access_sensitive_information = True
        )
        db.session.add(role)
        db.session.commit()

    admin_role = db.session.scalars(
        select(Role).filter_by(name="admin")        
    ).first()

    admin_username = os.getenv("ADMIN_USERNAME")
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")
    if not db.session.scalars(select(User).filter((User.username==admin_username) | (User.email==admin_email))).first():
        
        admin = User(
            username = admin_username,
            email = admin_email,
            password = admin_password,
            role = admin_role
        )

        db.session.add(admin)
        db.session.commit()
