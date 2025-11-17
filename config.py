import os
from dotenv import load_dotenv
import mailerlite as MailerLite

load_dotenv()

class Config:
    MAIL_KEY=os.environ.get("MAIL_KEY")
    DATABASE_URL = os.environ.get("DATABASE_URL")

    mail_client = MailerLite.Client({
        'api_key': MAIL_KEY
    })


    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    

