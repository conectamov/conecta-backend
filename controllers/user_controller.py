from flask import Blueprint, request
from factory import api, db

user_blueprint = Blueprint('user-blueprint', __name__, url_prefix="/user")

@user_blueprint.post("/subscribe")
@api.validate(
    tags=["user"]
)
def subscribe():
    """
        Subscribe new user on the newsletter
    """
    data = request.json



    