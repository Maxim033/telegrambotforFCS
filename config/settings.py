import os
import logging
from dotenv import load_dotenv

class BotConfig:
    def __init__(self):
        load_dotenv()
        self.openai_key = os.getenv('OPENAI_API_KEY')
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )
