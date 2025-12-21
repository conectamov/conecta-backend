from factory import db, api
from flask import Blueprint, request
from services.bot_session_service import check_interests, send_message, request_match, find_matching_users


bot_blueprint = Blueprint('bot-blueprint', __name__, url_prefix="/bot")


@bot_blueprint.post("/webhook")
@api.validate(
    tags=["bot"]
)
def whatsapp_webhook():
    data = request.get_json()
    payload = data.get("payload", {})
    
    chat_id = data["payload"]["from"]

    if payload["fromMe"] == True:
        return "", 200
    if chat_id.endswith("@g.us"):
        return {"status": "Ignored event"}, 200
    
    
    #check_interests(chat_id, payload["body"])
    #return "",200

    #sempre encontra usuário
    #current_user = db.session.scalars(
     #   select(UserAnswer).filter_by(number=current_phone)
    #).first()
    
    #if not found:
     #   check_interests(chat_id, payload["body"])
      #  return {"status": "User redirected to check_interests"}, 200


    #mockado
    current_user = mock_users[1]
    if "match" in payload["body"].lower():
        page = 0
        for c in payload["body"]:
            if c.isdigit():
                page = int(c) - 1
                break
        find_matching_users(chat_id, mock_users[0], page)
        return "", 200
    elif "conectar" in payload["body"].lower():
        id = 0
        for c in payload["body"]:
            if c.isdigit():
                id = int(c)
                break

        #aqui search requested pelo id na db
        request_to = mock_users[1]

        if not request_to:
            send_message(chat_id, "Desculpe, não conseguimos encontrar esse usuário, tente novamente com outra pessoa!")
            return {"status": "OK"}, 200
        
        if not request_to.matching:
            send_message(chat_id, BotResponses.user_matching_unavailable())
            return {"status": "OK"}, 200

        #mockado: faz a busca na db para saber se há um pending_request entre current_user e usuário de id do dígito 
        pending_request = True

        if pending_request:
            match(chat_id, request_to)
            #apaga o request
            return "", 200
        
        send_message(chat_id, BotResponses.match_has_been_sent())
        request_match(current_user, request_to)
        return "", 200
    else:
        help(chat_id, current_user, 1)
        return {"status": "OK"}, 200


