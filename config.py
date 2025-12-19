import os
from dotenv import load_dotenv
import mailerlite as MailerLite
from datetime import timedelta

load_dotenv()


class Config:
    MAIL_KEY = os.getenv("MAIL_KEY")
    DATABASE_URL = os.getenv("DATABASE_URL")

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    BOT_KEY = os.getenv("WAHA_API_KEY")

    mail_client = MailerLite.Client({"api_key": MAIL_KEY})

    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    FLASK_DEBUG = os.getenv("FLASK_DEBUG") or False
    SESSION_TYPE = "filesystem"
