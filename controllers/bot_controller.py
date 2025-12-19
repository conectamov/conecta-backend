from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from models.bot import UserAnswer, MatchQuestion

bot_blueprint = Blueprint("bot-blueprint", __name__, url_prefix="/bot")


@bot_blueprint.get("/")
def get_all():
    return {"success": True}

bot_blueprint = Blueprint('bot-blueprint', __name__, url_prefix="/bot")

#default settings
url = "http://localhost:3000/api/sendText"
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "X-Api-Key": Config.BOT_KEY
}

#functions
def send_message(phoneNumber, content):
    data = {
        "chatId": phoneNumber + "@c.us",
        "text": content,
        "session": "default"
    }

    try: 
        requests.post(url, json=data, headers=headers)
        print("deu!")
    except Exception as e:
        return {"msg": f"Something went wrong while trying to send message: {str(e)}"}, 400
    


@bot_blueprint.post("/")
def whatsapp_webhook():
    data = request.get_json()
    payload = data.get("payload", {})
    
    chat_id = data["payload"]["from"]

    if payload["fromMe"] == True:
        return "", 200
    if chat_id.endswith("@g.us"):
        return {"status": "Ignored event"}, 200
    
    
    response = {
        "chatId": chat_id,
        "text": "Working",
        "session": "default"
    }   

    requests.post(url, json=response, headers=headers)
    return {"status": "OK"}, 200
>>>>>>> 1796fbd (feat: added bot_controller.py)
