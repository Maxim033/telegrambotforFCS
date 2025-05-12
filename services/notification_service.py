import schedule
import time
import threading
from datetime import datetime
import logging


class NotificationService:
    def __init__(self, bot):
        self.bot = bot
        self.user_states = {}

    def send_weekly_notification(self):
        try:
            from services.vsu_service import VSUService
            week_type = VSUService.get_week_type()
            next_monday = datetime.now().date()

            while next_monday.weekday() != 0:
                next_monday = next_monday.replace(day=next_monday.day + 1)

            message = f"🔔 Напоминание: следующая неделя ({next_monday.strftime('%d.%m.%Y')}) - {week_type}"

            for user_id in list(self.user_states.keys()):
                try:
                    self.bot.send_message(user_id, message)
                except Exception as e:
                    logging.error(f"Ошибка отправки уведомления: {e}")
                    del self.user_states[user_id]
        except Exception as e:
            logging.error(f"Ошибка в send_weekly_notification: {e}")

    def start_scheduler(self):
        schedule.every().saturday.at("18:00").do(self.send_weekly_notification)
        threading.Thread(target=self._run_scheduler, daemon=True).start()

    def _run_scheduler(self):
        while True:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                logging.error(f"Ошибка планировщика: {e}")
                time.sleep(10)