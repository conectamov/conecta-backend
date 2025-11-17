import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MAIL_KEY=os.environ.get("MAIL_KEY")
    DATABASE_URL = os.environ.get("DATABASE_URL")

    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    

