import os
import logging
from dotenv import load_dotenv


load_dotenv()
logger = logging.getLogger(__name__)


TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# ConversationHandler bosqichlari
PHONE, WAITING_FOR_CODE = range(2)