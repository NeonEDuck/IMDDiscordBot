import os
from dotenv import load_dotenv
load_dotenv()

TOKEN  :str  = os.getenv('BOT_TOKEN', '')
REPLIT :bool = os.getenv('REPLIT', 'FALSE').lower() == 'true'