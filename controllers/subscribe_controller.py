from flask import Blueprint, request

subscribe_blueprint = Blueprint('subscribe-blueprint', __name__, url_prefix="/sub")

@subscribe_blueprint.post("/")

def subscribe():
    """
        Subscribe new user on the newsletter
    """
    data = request.json

    