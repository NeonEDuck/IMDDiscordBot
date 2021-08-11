import os
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')
REPLIT = os.getenv('REPLIT').lower() == 'true'