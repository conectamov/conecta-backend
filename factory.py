from flask import Flask, request, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from config import Config
from spectree import SpecTree, SecurityScheme
from sqlalchemy import select

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
    
    CORS(app, 
         supports_credentials=True, 
         origins=[
             "https://conecta-frontend.vercel.app",
             "http://localhost:5173",
             "http://127.0.0.1:5173"  
         ],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         allow_headers=["Content-Type", "Authorization", "X-Requested-With", "Accept", "Origin"]
    )

    @app.after_request
    def after_request(response):
        # These headers will be added by CORS, but you can keep this for additional headers
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Max-Age', '86400')
        return response

    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            response = make_response()
            response.headers.add("Access-Control-Allow-Origin", 
                               "https://conecta-frontend.vercel.app")
            response.headers.add("Access-Control-Allow-Methods", 
                               "GET, PUT, POST, DELETE, OPTIONS")
            response.headers.add("Access-Control-Allow-Headers", 
                               "Origin, X-Requested-With, Content-Type, Accept, Authorization")
            response.headers.add("Access-Control-Allow-Credentials", "true")
            return response

    api.register(app)
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    from models import User
    @jwt.user_lookup_loader
    def user_load(header, data):
        current_user = db.session.scalars(
            select(User).filter_by(username=data["sub"])
        ).first()
        return current_user

    from controllers import subscriber_blueprint, user_blueprint, auth_blueprint, post_blueprint, role_blueprint
    app.register_blueprint(subscriber_blueprint)
    app.register_blueprint(user_blueprint)
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(post_blueprint)
    app.register_blueprint(role_blueprint)

    return app
