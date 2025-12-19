from flask import Flask, request, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from config import Config
from spectree import SpecTree, SecurityScheme
from sqlalchemy import select
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_admin import Admin
from flask_admin.theme import Bootstrap4Theme
from admin.admin import start_admin_views
from sqlmodel import SQLModel, create_engine


db = SQLAlchemy()
migrate = Migrate()
api = SpecTree(
    "flask",
    title="Conecta API",
    path="docs",
    version="v1.0",
    security_schemes=[
        SecurityScheme(
            name="BearerAuth",
            data={"type": "http", "scheme": "bearer", "bearerFormat": "JWT"},
        )
    ],
)
jwt = JWTManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)
    CORS(
        app,
        supports_credentials=True,
        origins=["https://conecta-frontend.vercel.app"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=[
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "Accept",
            "Origin",
        ],
    )

    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            response = make_response()
            response.headers[
                "Access-Control-Allow-Origin"
            ] = "https://conecta-frontend.vercel.app"
            response.headers[
                "Access-Control-Allow-Methods"
            ] = "GET, PUT, POST, DELETE, OPTIONS"
            response.headers[
                "Access-Control-Allow-Headers"
            ] = "Origin, X-Requested-With, Content-Type, Accept, Authorization"
            response.headers["Access-Control-Allow-Credentials"] = "true"
            return response

    @app.after_request
    def after_request(response):
        response.headers.setdefault("Access-Control-Allow-Credentials", "true")
        response.headers.setdefault("Access-Control-Max-Age", "86400")
        response.headers[
            "Strict-Transport-Security"
        ] = "max-age=15768000; includeSubDomains"
        return response

    api.register(app)
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    from models.role import Role
    from models.user import User
    from models.post import Post

    app.engine = create_engine(app.config.get("DATABASE_URL"), echo=True)
    SQLModel.metadata.create_all(
        app.engine,
    )

    if app.config.get("FLASK_DEBUG"):
        app.secret_key = "12345678"

        admin = Admin(
            app,
            name="Conecta Panel",
            theme=Bootstrap4Theme(
                swatch="darkly",
            ),
        )
        start_admin_views(admin, db)

    @jwt.user_lookup_loader
    def user_load(header, data):
        from models.user import User

        return db.session.scalars(select(User).filter_by(username=data["sub"])).first()

<<<<<<< HEAD
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
        from models.user import TokenBlocklist
=======
    from controllers import (
        subscriber_blueprint,
        user_blueprint,
        auth_blueprint,
        post_blueprint,
        role_blueprint,
        bot_blueprint,
    )
>>>>>>> 1796fbd (feat: added bot_controller.py)

        jti = jwt_payload["jti"]
        token = db.session.query(TokenBlocklist.id).filter_by(jti=jti).scalar()

        return token is not None

    from controllers.auth_controller import auth_blueprint
    from controllers.user_controller import user_blueprint
    from controllers.role_controller import role_blueprint
    from controllers.subscriber_controller import subscriber_blueprint
    from controllers.post_controller import post_blueprint
    from controllers.bot_controller import bot_blueprint

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(role_blueprint)
    app.register_blueprint(subscriber_blueprint)
    app.register_blueprint(user_blueprint)
    app.register_blueprint(post_blueprint)
<<<<<<< HEAD
=======
    app.register_blueprint(role_blueprint)
>>>>>>> 1796fbd (feat: added bot_controller.py)
    app.register_blueprint(bot_blueprint)

    return app
