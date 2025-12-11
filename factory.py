from config import Config
from spectree import SpecTree, SecurityScheme
from sqlalchemy import select
from werkzeug.middleware.proxy_fix import ProxyFix

db = SQLAlchemy()
migrate = Migrate()
@@ -16,11 +17,11 @@
    version="v1.0",
    security_schemes=[
        SecurityScheme(
            name="BearerAuth",  
            name="BearerAuth",
            data={
                "type": "http",     
                "scheme": "bearer",   
                "bearerFormat": "JWT" 
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT"
            }
        )
    ]
@@ -31,38 +32,32 @@ def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)

    CORS(app, 
         supports_credentials=True, 
         origins=[
             "https://conecta-frontend.vercel.app"
         ],
    CORS(app,
         supports_credentials=True,
         origins=["https://conecta-frontend.vercel.app"],
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
@@ -71,10 +66,9 @@ def handle_preflight():
    from models import User
    @jwt.user_lookup_loader
    def user_load(header, data):
        current_user = db.session.scalars(
        return db.session.scalars(
            select(User).filter_by(username=data["sub"])
        ).first()
        return current_user

    from controllers import subscriber_blueprint, user_blueprint, auth_blueprint, post_blueprint, role_blueprint
    app.register_blueprint(subscriber_blueprint)
