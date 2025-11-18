from factory import db

class Role(db.Model):
    __tablename__ = "role"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    cam_manage_users = db.Column(db.Boolean, default=False)
    cam_manage_subscriptions = db.Column(db.Boolean, default=False)
    cam_create_posts = db.Column(db.Boolean, default=False),
    cam_manage_posts = db.Column(db.Boolean, default=False),


    def __repr__(self) -> str:
        return f"Role {self.name}"