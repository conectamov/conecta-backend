import requests
from factory import db
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from models.bot import UserAnswer, MatchQuestion
from config import Config
from sqlalchemy import select

bot_blueprint = Blueprint("bot-blueprint", __name__, url_prefix="/bot")


@bot_blueprint.get("/")
def get_all():
    return {"success": True}

bot_blueprint = Blueprint('bot-blueprint', __name__, url_prefix="/bot")

#default settings
send_text = "http://localhost:3000/api/sendText"
send_pool = "http://localhost:3000/api/sendPool"
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "X-Api-Key": Config.BOT_KEY
}


def send_message(chat_id, content):
    data = {
        "chatId": chat_id,
        "text": content,
        "session": "default"
    }   

    requests.post(send_text, json=data, headers=headers)

def user_match(chat_id):
    send_message(chat_id, "Matching!")

def help(chat_id):
    send_message(chat_id, "Essa é nossa mensagem de ajuda.")

def check_interests(chat_id):
    send_message(chat_id, "Cadastrando seus interesses!")


@bot_blueprint.post("/")
def whatsapp_webhook():
    data = request.get_json()
    payload = data.get("payload", {})
    
    chat_id = data["payload"]["from"]

    if payload["fromMe"] == True:
        return "", 200
    if chat_id.endswith("@g.us"):
        return {"status": "Ignored event"}, 200
    
    current_phone = "".join(c for c in chat_id if c.isdigit())

    found = db.session.scalars(
        select(UserAnswer).filter_by(number=current_phone)
    ).first()
    
    if not found:
        check_interests(chat_id)
        return {"status": "User redirected to check_interests"}, 200


    if "match" in payload["body"].lower():
        user_match()
    else:
        send_message(chat_id, "Não entendi sua mensagem.. Mas não se preocupe! Estou te enviando instruções.")
        help(chat_id)



    response = {    
        "chatId": chat_id,
        "text": "Usuário encontrado!",
        "session": "default"
    }   

    requests.post(send_text, json=response, headers=headers)
    return {"status": "OK"}, 200
