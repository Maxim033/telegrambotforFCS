import telebot
from telebot import types
from datetime import datetime
import logging
from services.ai_service import AIAssistant
from services.vsu_service import VSUService
from services.notification_service import NotificationService


class VSUBot:
    def __init__(self, token, openai_key):
        self.bot = telebot.TeleBot(token)
        self.ai_assistant = AIAssistant(openai_key)
        self.notification_service = NotificationService(self.bot)
        self._register_handlers()

    def _register_handlers(self):
        @self.bot.message_handler(commands=['start', 'menu'])
        def handle_start(message):
            self._handle_start(message)

        @self.bot.message_handler(func=lambda m: True)
        def handle_all_messages(message):
            self._handle_all_messages(message)

        @self.bot.callback_query_handler(func=lambda c: True)
        def handle_callbacks(call):
            self._handle_callbacks(call)

    def _handle_start(self, message):
        try:
            name = message.from_user.first_name
            self.bot.send_message(message.chat.id, f"👋 Привет, {name}! Я бот ВГУ.")
            self._show_main_menu(message.chat.id)
        except Exception as e:
            logging.error(f"Ошибка в handle_start: {e}")

    def _show_main_menu(self, chat_id):
        menu = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        buttons = [
            '🏫 Корпуса ВГУ',
            '📅 Числитель/знаменатель',

        ]
        menu.add(*buttons)
        self.bot.send_message(chat_id, "Выберите пункт:", reply_markup=menu)

    def _handle_all_messages(self, message):
        try:
            text = message.text.lower()
            if text == '🏫 корпуса вгу':
                self._show_buildings(message)
            elif text == '📅 числитель/знаменатель':
                self._show_week_type(message)

        except Exception as e:
            logging.error(f"Ошибка обработки сообщения: {e}")
            self.bot.send_message(message.chat.id, "⚠️ Произошла ошибка. Попробуйте позже.")

    def _show_buildings(self, message):
        try:
            buildings = VSUService.get_buildings_info()
            response = "🏫 Корпуса ВГУ:\n\n"
            for name, info in buildings.items():
                response += f"{name}\nАдрес: {info['address']}\nСсылка: {info['yandex_maps_link']}\n\n"
            self.bot.send_message(message.chat.id, response)
        except Exception as e:
            logging.error(f"Ошибка показа корпусов: {e}")

    def _show_week_type(self, message):
        try:
            week_type = VSUService.get_week_type()
            next_monday = datetime.now().date()
            while next_monday.weekday() != 0:
                next_monday = next_monday.replace(day=next_monday.day + 1)

            response = f"Следующая неделя ({next_monday.strftime('%d.%m.%Y')}) - {week_type}"
            self.bot.send_message(message.chat.id, response)
        except Exception as e:
            logging.error(f"Ошибка показа типа недели: {e}")

    def run(self):
        try:
            self.notification_service.start_scheduler()
            logging.info("Бот запущен")
            self.bot.infinity_polling()
        except Exception as e:
            logging.error(f"Ошибка запуска бота: {e}")