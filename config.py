import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MAIL_KEY=os.environ.get("MAIL_KEY")