import os
from dotenv import load_dotenv
import mailerlite as MailerLite

load_dotenv()

class Config:
    MAIL_KEY=os.getenv("MAIL_KEY")
    DATABASE_URL = os.getenv("DATABASE_URL")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    OPENAI_KEY = os.getenv("OPENAI_KEY")
    BOT_KEY = os.getenv("WAHA_API_KEY")

    mail_client = MailerLite.Client({
        'api_key': MAIL_KEY
    })


    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    

