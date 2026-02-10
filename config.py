import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
MAX_HISTORY_MESSAGES = int(os.getenv("MAX_HISTORY_MESSAGES", 20))