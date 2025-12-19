from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from models.bot import UserAnswer, MatchQuestion

bot_blueprint = Blueprint("bot-blueprint", __name__, url_prefix="/bot")


@bot_blueprint.get("/")
def get_all():
    return {"success": True}
