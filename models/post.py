from factory import db
from datetime import datetime, timezone

class Post(db.Model):
    __tablename__ = "post"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Unicode(256), nullable=False)
    content = db.Column(db.UnicodeText, nullable=False)
    created_at = db.Column(db.DateTime, default = lambda: datetime.now(timezone.utc))

    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    author = db.relationship("User", back_populates="posts")

    def __repr__(self) -> str:
        return f"Post {self.id} by {self.author.username}"