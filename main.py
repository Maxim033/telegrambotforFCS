from config.settings import BotConfig
from bot.vsu_bot import VSUBot
import logging

if __name__ == "__main__":
    try:
        config = BotConfig()
        bot = VSUBot(
            token=config.telegram_token,
            openai_key=config.openai_key
        )
        bot.run()  # ✅ просто обычный вызов
    except Exception as error:
        logging.error(f"Фатальная ошибка: {error}")
