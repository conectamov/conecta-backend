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


db = SQLAlchemy()
migrate = Migrate()
api = SpecTree(
    'flask',
    title="Conecta API",
    path="docs",
    version="v1.0",
    security_schemes=[
        SecurityScheme(
            name="BearerAuth",
            data={
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT"
            }
        )
    ]
)
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    from models import User

    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)

    CORS(app,
         supports_credentials=True,
         origins=["https://conecta-frontend.vercel.app"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         allow_headers=["Content-Type", "Authorization", "X-Requested-With", "Accept", "Origin"]
    )

    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            response = make_response()
            response.headers["Access-Control-Allow-Origin"] = "https://conecta-frontend.vercel.app"
            response.headers["Access-Control-Allow-Methods"] = "GET, PUT, POST, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Origin, X-Requested-With, Content-Type, Accept, Authorization"
            response.headers["Access-Control-Allow-Credentials"] = "true"
            return response

    @app.after_request
    def after_request(response):
        response.headers.setdefault('Access-Control-Allow-Credentials', 'true')
        response.headers.setdefault('Access-Control-Max-Age', '86400')
        response.headers['Strict-Transport-Security'] = 'max-age=15768000; includeSubDomains'
        return response

    api.register(app)
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    if(app.config.get("FLASK_DEBUG")):
        admin = Admin(app, name='Conecta Panel', theme=Bootstrap4Theme(swatch='darkly',))
        start_admin_views(admin, db)

    @jwt.user_lookup_loader
    def user_load(header, data):
        return db.session.scalars(
            select(User).filter_by(username=data["sub"])
        ).first()

    from controllers import subscriber_blueprint, user_blueprint, auth_blueprint, post_blueprint, role_blueprint
    app.register_blueprint(subscriber_blueprint)
    app.register_blueprint(user_blueprint)
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(post_blueprint)
    app.register_blueprint(role_blueprint)

    return app