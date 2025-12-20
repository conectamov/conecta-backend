import requests
import random
from factory import db, api
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from config import Config
from sqlalchemy import select
from utils.tags import tags
from services.embed_service import EmbedService
from services.similarity_service import SimilarityService
from dataclasses import dataclass

bot_blueprint = Blueprint('bot-blueprint', __name__, url_prefix="/bot")

#user answer mockado
class UserAnswerPost():
    id: int
    name: str
    number: str
    matching: bool
    answers: list[int] | None

@dataclass
class UserAnswer():
    id: int 
    name: str
    number: str
    matching: bool
    newsletter: bool
    answers: list[int] | None
    embed: list[float] | None

@dataclass
class Session:
    phone: str
    step: str = "ASK_NAME"
    ask_fullname: str = ""
    ask_subjects: str = ""
    ask_level: str = ""
    ask_interests: str = ""
    ask_opportunities: str = ""
    ask_matching: str = ""

#usuarios mockados
mock_users = [
    UserAnswer(
        id=1,
        name="Otávio",
        number="5538988252013",
        matching=True,
        newsletter=True,
        answers=[0, 3, 12, 27, 45],  # ex: olimpíadas, matemática, exatas, estudo diário
        embed=[
            0.12, 0.08, 0.31, 0.44, 0.09,
            0.02, 0.18, 0.27
        ]
    ),
    UserAnswer(
        id=2,
        name="Maria",
        number="5538999111222",
        matching=True,
        newsletter=True,
        answers=[1, 7, 18, 33, 60],  # ex: exterior, intercâmbio, inglês, liderança
        embed=[
            0.05, 0.41, 0.22, 0.09, 0.33,
            0.14, 0.06, 0.18
        ]
    ),
    UserAnswer(
        id=3,
        name="Augustus",
        matching=True,
        newsletter=True,
        number="553398335988",
        answers=[2, 9, 21, 45, 88],  # ex: oportunidades, tecnologia, programação
        embed=[
            0.29, 0.17, 0.11, 0.36, 0.04,
            0.21, 0.08, 0.13
        ]
    ),
]


#routes
@bot_blueprint.post("/")    
@api.validate(
    tags=["bot"],
)
def register_user():
    """
    Register users based on interests
    """
    data = request.json

    userEmbed = EmbedService.user_vector_from_indices(data["answers"])

    #agora cria o usuário abaixo com os dados e o embed
    newUser = UserAnswer(
        id=data["id"],
        number=data["number"],
        answers=data["answers"],
        matching=True,
        newsletter=True,
        embed=userEmbed
    )


#default settings
send_text = "http://localhost:3000/api/sendText"
send_pool = "http://localhost:3000/api/sendPool"
send_contact = "http://localhost:3000/api/sendContactVcard"
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

def compatibility_emoji(score: float) -> str:
    if score >= 0.8:
        return "🔥"
    if score >= 0.5:
        return "✨"
    return "🤝"

def generate_matching(chat_id: str, current_user: UserAnswer, page:int):
    matching: list[tuple[UserAnswer, float]] = []

    for user in mock_users:
        if user.id == current_user.id:
            continue
        if not user.embed:
            continue

        coef = SimilarityService.cosine_similarity(
            user.embed,
            current_user.embed
        )
        matching.append((user, coef))

    matching.sort(key=lambda x: x[1], reverse=True)


    header_options = [
        "✨ Conexões que podem acelerar sua jornada de estudos:",
        "🚀 Pessoas que compartilham interesses com você:",
        "🌱 Pessoas alinhadas com o que você quer aprender:",
    ]


    lines = [random.choice(header_options)]

    per_page = 4

    start = page
    end = start + per_page

    message = (
        "😕 Não encontramos conexões nessa página.\n\n"
        "Tente outra página ou envie *match* novamente "
        "para explorar mais pessoas ✨"
    )
    if len(matching[start:end]) != 0:
        for user, score in matching[start:end]:  
            if not user.matching: 
                continue  
            percent = int(score * 100)
            emoji = compatibility_emoji(score)
            lines.append(
                f"{emoji} *{user.name}*\n"
                f"• Compatibilidade: *{percent}%*\n"
                f"• Para se conectar, envie: *conectar {user.id}*\n"
            )

        
        lines.append(f"📄 Página {start + 1}")
        message = "\n".join(lines)

    send_message(chat_id, message)
    send_message(
        chat_id,
        "🔎 Quer ver outra página?\n"
        "Envie: *match 2*, *match 3*, etc."
    )


def request_match(user: UserAnswer, requested: UserAnswer):
    chat_id_requested = requested.number + "@c.us"

    percent = int(SimilarityService.cosine_similarity(user.embed, requested.embed)*100)

    message = (
        "✨ Você recebeu um pedido de conexão no Conecta!\n\n"
        f"👤 *{user.name}*\n"
        f"🤝 Compatibilidade de interesses: *{percent}%*\n\n"
        "👉 Para aceitar, envie:\n"
        f"*conectar {user.id}*"
    )


    send_message(chat_id_requested, message)

def match(chat_id: str, user):
    whatsappId = user.number

    phoneNumber = f"+{whatsappId}"

    data = {
        "session": "default",
        "chatId": chat_id,
        "contacts": [
            {
                "fullName": f"{user.name}",
                "organization": "CONECTA user",
                "phoneNumber": f"{phoneNumber}",
                "whatsappId": f"{whatsappId}"
            }
        ]
    }

    message = (
        f"🎉 Conexão criada com *{user.name}*!\n\n"
        "Agora vocês já podem conversar e trocar ideias 💬\n"
        "Comece enviando uma mensagem agora mesmo 🚀"
    )

    send_message(chat_id, message)
    requests.post(send_contact, json=data, headers=headers)

def help(chat_id, type):
    if type == 0:
        message = (
            "👋 Ei! Seja bem-vindo ao Conecta.\n\n"
            "Aqui você encontra pessoas com interesses parecidos com os seus nos estudos, "
            "projetos e oportunidades — para se inspirar, trocar ideias e crescer junto ✨\n\n"
            "👉 Para começar, envie:\n"
            "*match*\n\n"
            "Eu vou te mostrar conexões que podem acelerar sua jornada 🚀"
        )

        send_message(chat_id, message)
        check_interests()
        return "", 200
    if type == 1:
        message = (
            "🤔 Não entendi muito bem essa mensagem.\n\n"
            "Aqui vão algumas coisas que você pode fazer:\n"
            "• Enviar *match* para ver pessoas com interesses parecidos\n"
            "• Enviar *match 2*, *match 3*, etc. para navegar pelas páginas\n"
            "• Enviar *conectar ID* para se conectar com alguém\n\n"
            "Se quiser começar do zero, é só mandar *match* ✨"
        )


        send_message(chat_id, message)
        return "", 200

# MOCK de sessão (simula banco)
mock_sessions = {}


def check_interests(chat_id, last_answer):
    phone = "".join(c for c in chat_id if c.isdigit())

    session = mock_sessions.get(phone)

    if not session:
        session = Session(phone=phone)
        mock_sessions[phone] = session
        send_message(chat_id, "Qual seu nome?")
        return

    if session.step == "ASK_NAME":
        session.ask_fullname = last_answer
        session.step = "ASK_SUBJECT"
        send_message(chat_id, "Quais são suas matérias favoritas?")
        return

    if session.step == "ASK_SUBJECT":
        session.ask_subjects = last_answer
        session.step = "ASK_LEVEL"
        send_message(chat_id, "Como você descreveria o seu nível atual como estudante?")
        return

    if session.step == "ASK_LEVEL":
        session.ask_level = last_answer
        session.step = "ASK_INTEREST"
        send_message(chat_id, "Quais são seus interesses no momento?")
        return

    if session.step == "ASK_INTEREST":
        session.ask_interests = last_answer
        session.step = "ASK_OPPORTUNITIES"
        send_message(chat_id, "Você gostaria de receber oportunidades que combinem com você?")
        return

    if session.step == "ASK_OPPORTUNITIES":
        session.ask_opportunities = last_answer
        session.step = "ASK_MATCHING"
        send_message(chat_id, "Você gostaria de se conectar com outros estudantes?")
        return

    if session.step == "ASK_MATCHING":
        session.ask_matching = last_answer
        session.step = "DONE"
        send_message(chat_id, "Analisando suas respostas, aguarde um momento.") 
        return
    if session.step == "DONE":
        #manda pro gpt
        #finish session
       
       
       
        send_message(chat_id, "Perfeito! Seu cadastro foi concluído 🚀")


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
     #   help(chat_id, 0)
      #  return {"status": "User redirected to check_interests"}, 200


    #mockado
    current_user = mock_users[1]
    print(payload)
    if "match" in payload["body"].lower():
        page = 0
        for c in payload["body"]:
            if c.isdigit():
                page = int(c) - 1
                break
        generate_matching(chat_id, mock_users[0], page)
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
            message = (
                "🚫 Essa pessoa não está disponível para conexões no momento.\n\n"
                "Mas não se preocupe! Existem outras pessoas incríveis "
                "que podem combinar com você.\n\n"
                "Envie *match* para continuar explorando ✨"
            )

    
            send_message(chat_id, message)
            return {"status": "OK"}, 200

        #mockado: faz a busca na db para saber se há um pending_request entre current_user e usuário de id do dígito 
        pending_request = True

        if pending_request:
            match(chat_id, request_to)
            #apaga o request
            return "", 200
        
        message = (
            "📨 Pedido de conexão enviado com sucesso!\n\n"
            "Agora é só aguardar 😊\n"
            "Assim que a pessoa aceitar, eu te aviso aqui mesmo.\n\n"
            "Enquanto isso, você pode enviar *match* para conhecer mais pessoas ✨"
        )

        send_message(chat_id, message)
        request_match(current_user, request_to)
        return "", 200
    else:
        help(chat_id, 1)
        return {"status": "OK"}, 200


