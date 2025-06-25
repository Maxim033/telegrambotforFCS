import aioschedule
import threading
import asyncio
import logging
from datetime import datetime, timedelta

class NotificationService:
    def __init__(self, bot):
        self.bot = bot
        self.user_ids = set()

    async def send_weekly_notification(self):
        from services.vsu_service import VSUService

        try:
            week_type = VSUService.get_week_type()
            next_monday = datetime.now().date()
            days_ahead = (7 - next_monday.weekday()) % 7
            next_monday += timedelta(days=days_ahead)

            message = f"🔔 Напоминание: следующая неделя ({next_monday.strftime('%d.%m.%Y')}) - {week_type}"

            for user_id in list(self.user_ids):
                try:
                    self.bot.send_message(user_id, message)
                except Exception as error:
                    logging.error(f"Ошибка отправки пользователю {user_id}: {error}")
                    self.user_ids.discard(user_id)
        except Exception as error:
            logging.error(f"Ошибка в send_weekly_notification: {error}")

    async def scheduler_loop(self):
        aioschedule.every().saturday.at("18:00").do(self.send_weekly_notification)
        while True:
            await aioschedule.run_pending()
            await asyncio.sleep(1)

    import threading

    def start_scheduler(self):
        def run_loop():
            asyncio.set_event_loop(asyncio.new_event_loop())
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.scheduler_loop())

        threading.Thread(target=run_loop, daemon=True).start()

