from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from config import Config
from spectree import SpecTree
from sqlalchemy import select

cors = CORS(support_credentials=True)
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
api = SpecTree(
    'flask',
    title="API-Conecta",
    path="docs",
    version="v1.0",
    security=[{"BearerAuth": []}]
)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    from models import User
    @jwt.user_lookup_loader
    def user_load(header, data):
        current_user = db.session.scalars(
            select(User).filter_by(username=data["sub"])
        ).first
        return current_user

    from controllers import subscriber_blueprint
    app.register_blueprint(subscriber_blueprint)

    return app
