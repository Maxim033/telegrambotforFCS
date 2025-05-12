from config.settings import BotConfig
from bot.vsu_bot import VSUBot

if __name__ == "__main__":
    try:
        config = BotConfig()
        bot = VSUBot(
            token=config.telegram_token,
            openai_key=config.openai_key
        )
        bot.run()
    except Exception as e:
        import logging
        logging.error(f"Фатальная ошибка: {e}")