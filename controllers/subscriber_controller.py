from config import Config
from flask import Blueprint, request
from factory import api, db
from pydantic import BaseModel
from spectree import Response
from utils import DefaultResponse
from sqlalchemy import select
from models import Subscriber

subscriber_blueprint = Blueprint('subscriber-blueprint', __name__, url_prefix="/sub")

class SubscribeModel(BaseModel): 
    name: str
    email: str

@subscriber_blueprint.post("/")
@api.validate(
    json=SubscribeModel,
    tags=["subscriber"],
    resp=Response(HTTP_200=DefaultResponse, HTTP_400=DefaultResponse, HTTP_500=DefaultResponse)
)
def subscribe():
    """
        Subscribe new user on the newsletter
    """
    data = request.json
    try:
        Config.mail_client.subscribers.create(data["email"], fields={'name':data["name"]})
    except:
        return {"msg": "Failed subscribing: the recipient address may be invalid or the mail service is unreachable."}, 500
    current = db.session.scalars(
        select(Subscriber).filter_by(email=data["email"])
    ).first()

    if current is None:
        subscriber = Subscriber(
            name = data["name"],
            email = data["email"]
        )

        try: 
            db.session.add(subscriber)
            db.session.commit()
        except:
            return {"msg": "Something went wrong!"}, 400
    return {"msg": "Subscribed successfuly!"}