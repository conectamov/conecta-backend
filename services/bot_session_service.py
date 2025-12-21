import requests
import random
from config import Config
from sqlalchemy import select
from utils.tags import tags
from services.embed_service import EmbedService
from services.similarity_service import SimilarityService
from dataclasses import dataclass
from services.gpt_classifier import classify_student
from utils.bot_responses import BotResponses

#classes mockadas
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
    name: str = ""
    subjects: str = ""
    level: str = ""
    interests: str = ""
    opportunities: bool = False
    matching: bool = False

@dataclass
class UserModel:
    phone: str
    tags: list[int]
    opportunities: bool = False
    matching: bool = False

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


#auxiliar
def compatibility_emoji(score: float) -> str:
    if score >= 0.8:
        return "🔥"
    if score >= 0.5:
        return "✨"
    return "🤝"


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


#functions

def register_user(incoming: UserModel):
    """
    Register incoming user data on database
    """

    userEmbed = EmbedService.user_vector_from_indices(incoming.tags)

    #agora cria o usuário abaixo com os dados e o embed
    newUser = UserAnswer(
        number=incoming.phone,
        answers=incoming["tags"],
        matching=True,
        newsletter=True,
        embed=userEmbed
    )

    #add na db


def find_matching_users(chat_id: str, current_user: UserAnswer, page:int):
    """
    List 
    """
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

    message = BotResponses.could_not_find_match()

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

    message = BotResponses.received_request_match(user)

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

    message = BotResponses.created_connection_success(user)

    send_message(chat_id, message)
    requests.post(send_contact, json=data, headers=headers)

def help(chat_id, user: UserAnswer, type):
    if type == 1:



        send_message(chat_id, message)
        return "", 200

# MOCK de sessão (simula banco)
mock_sessions = {}

def check_interests(chat_id, last_answer):
    phone = "".join(c for c in chat_id if c.isdigit())

    session : Session = mock_sessions.get(phone)

    if not session:
        send_message(chat_id, BotResponses.welcome_message(user))
        session = Session(phone=phone)
        mock_sessions[phone] = session
        send_message(chat_id, BotResponses.ask_name())
        return

    if session.step == "ASK_NAME":
        session.name = last_answer
        session.step = "ASK_SUBJECT"
        send_message(chat_id, BotResponses.ask_subjects())
        return

    if session.step == "ASK_SUBJECT":
        session.subjects = last_answer
        session.step = "ASK_LEVEL"
        send_message(chat_id, BotResponses.ask_level())
        return

    if session.step == "ASK_LEVEL":
        session.level = last_answer
        session.step = "ASK_INTEREST"
        send_message(chat_id, BotResponses.ask_interest())
        return

    if session.step == "ASK_INTEREST":
        session.interests = last_answer
        session.step = "ASK_OPPORTUNITIES"
        send_message(chat_id, BotResponses.ask_opportunities())
        return

    if session.step == "ASK_OPPORTUNITIES":
        if not "sim" in last_answer.lower() and not "não" in last_answer.lower():
            send_message(chat_id, BotResponses.yes_or_no_answer())
            send_message(chat_id, BotResponses.ask_opportunities_2())
            return

        if "sim" in last_answer.lower():
            session.opportunities = True

        session.step = "ASK_MATCHING"
        send_message(chat_id, BotResponses.ask_matching())
        return


    if session.step == "ASK_MATCHING":
        if not "sim" in last_answer.lower() and not "não" in last_answer.lower():
            send_message(chat_id, BotResponses.yes_or_no_answer())
            send_message(chat_id, BotResponses.ask_matching_2())
            return

        if "sim" in last_answer.lower():
            session.matching = True

        send_message(chat_id, BotResponses.analysing_answers())
       
        #Retorna a lista de tags   
        classified = classify_student(session)

        if not classified["appropriate"]:
            send_message(chat_id, BotResponses.inappropriated_answer())

            #finish session 
            #simlula finish session
            mock_sessions.pop(phone)
            
            return

        send_message(chat_id, BotResponses.created_profile_success(session.name))
        #finish session

        #simulando final:
        mock_sessions.pop(phone)

        #efetiva usuário obtido
        new_user = UserModel(
            phone=phone,
            tags=classified["tags"],
            opportunities=session.opportunities,
            matching=session.matching
        )
        register_user(new_user)

        #teste:
        #tags_string = ", ".join(tags[i] for i in classified["tags"])
        #send_message(chat_id, tags_string)