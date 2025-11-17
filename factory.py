from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from config import Config
from spectree import SpecTree

cors = CORS(support_credentials=True)
db = SQLAlchemy()
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

    return app
