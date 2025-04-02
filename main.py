import os
import telebot
from telebot import types
import openai
import schedule
import time
import threading
from datetime import datetime
import logging
from dotenv import load_dotenv

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Загрузка переменных окружения
load_dotenv()

# Инициализация API
openai.api_key = os.getenv('OPENAI_API_KEY')
bot = telebot.TeleBot(os.getenv('TELEGRAM_BOT_TOKEN'))

# Словарь для хранения состояний пользователей
user_states = {}

# Информация о корпусах ВГУ
vsu_buildings = {
    'Главный корпус': {
        'address': 'Университетская площадь 1, Воронеж',
        'yandex_maps_link': 'https://yandex.ru/maps/?text=Университетская+площадь+1,+Воронеж'
    },
    'Второй корпус': {
        'address': 'Улица Ленина 10, Воронеж',
        'yandex_maps_link': 'https://yandex.ru/maps/?text=Улица+Ленина+10,+Воронеж'
    },
    'Третий корпус': {
        'address': 'Проспект Революции 24, Воронеж',
        'yandex_maps_link': 'https://yandex.ru/maps/?text=Проспект+Революции+24,+Воронеж'
    },
    'Пятый корпус': {
        'address': 'Улица Хользунова 40, Воронеж',
        'yandex_maps_link': 'https://yandex.ru/maps/?text=Улица+Хользунова+40,+Воронеж'
    },
    'Шестой корпус': {
        'address': 'Улица Хользунова 40а, Воронеж',
        'yandex_maps_link': 'https://yandex.ru/maps/?text=Улица+Хользунова+40а,+Воронеж'
    }
}


def generate_response(user_query, context):
    """Генерация ответа с использованием OpenAI."""
    try:
        messages = [
            {"role": "system", "content": context},
            {"role": "user", "content": user_query}
        ]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=400,
            temperature=0.7
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        logging.error(f"Ошибка OpenAI: {e}")
        return None


def get_week_type():
    """Определяет, числитель или знаменатель на следующей неделе."""
    now = datetime.now()
    if now.month == 9 and 1 <= now.day <= 7:  # Первая неделя сентября
        return "числитель"

    week_number = now.isocalendar()[1]
    return "числитель" if week_number % 2 == 1 else "знаменатель"


@bot.message_handler(commands=['start', 'menu'])
def handle_start(message):
    """Обработка команд /start и /menu."""
    user_name = message.from_user.first_name
    if message.text == '/start':
        bot.send_message(message.chat.id, f"👋 Привет, {user_name}! Я информационный бот ВГУ.")
    send_main_menu(message.chat.id)


def send_main_menu(chat_id):
    """Отправляет главное меню."""
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        '🏫 Корпуса ВГУ',
        '🧭 Аудитории главного корпуса',
        '📰 Новости факультета',
        '⚽ Спортивные команды',
        '🤖 Задать вопрос ИИ',
        '📅 Числитель/знаменатель',
        '🧹 Очистить чат'
    ]
    keyboard.add(*buttons)
    bot.send_message(chat_id, "Выберите нужный пункт меню:", reply_markup=keyboard)


@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    """Обработка текстовых сообщений."""
    text = message.text.lower()

    if text == '🏫 корпуса вгу':
        handle_building_locations(message)
    elif text == '🧭 аудитории главного корпуса':
        handle_classroom_instructions(message)
    elif text == '📰 новости факультета':
        handle_faculty_news(message)
    elif text == '⚽ спортивные команды':
        handle_sports_teams(message)
    elif text == '🤖 задать вопрос ии':
        bot.send_message(message.chat.id, "Напишите ваш вопрос, и я постараюсь на него ответить:")
        bot.register_next_step_handler(message, handle_ai_query)
    elif text == '📅 числитель/знаменатель':
        handle_week_type(message)
    elif text == '🧹 очистить чат':
        handle_clear_chat(message)
    else:
        bot.send_message(message.chat.id, "Я не понимаю вашего запроса. Пожалуйста, используйте меню.",
                         reply_markup=create_main_menu())


def handle_building_locations(message):
    """Обработка запроса на расположение корпусов."""
    response = "🏫 Корпуса ВГУ:\n\n"
    for building, info in vsu_buildings.items():
        response += f"<b>{building}</b>\nАдрес: {info['address']}\n[Открыть в Яндекс.Картах]({info['yandex_maps_link']})\n\n"

    bot.send_message(message.chat.id, response, parse_mode="HTML", disable_web_page_preview=True)


def handle_classroom_instructions(message):
    """Обработка запроса на инструкции по аудиториям."""
    response = ("🧭 Как найти аудитории в главном корпусе:\n\n"
                "1. Первая цифра номера аудитории - это этаж (например, 202 - второй этаж)\n"
                "2. Схема корпуса: https://drive.google.com/file/d/1FFqGDxrR2L-E4Bpb-jybSCw2kyX9tQJy/view?usp=sharing")
    bot.send_message(message.chat.id, response)


def handle_faculty_news(message):
    """Обработка запроса на новости факультета."""
    response = ("📰 Актуальные новости факультета:\n\n"
                "• Официальная группа для абитуриентов: https://vk.com/fknabitur\n"
                "• Новости ФКН: https://vk.com/cs_vsu")
    bot.send_message(message.chat.id, response)


def handle_sports_teams(message):
    """Обработка запроса на спортивные команды."""
    response = ("⚽ Спортивные секции ВГУ:\n\n"
                "Все спортивные направления ВГУ: https://vk.com/bobry_vsu\n"
                "Здесь вы найдёте информацию о всех секциях и соревнованиях.")
    bot.send_message(message.chat.id, response)


def handle_week_type(message):
    """Обработка запроса на числитель/знаменатель."""
    week_type = get_week_type()
    next_monday = datetime.now().date()

    # Находим ближайший понедельник
    while next_monday.weekday() != 0:
        next_monday = next_monday.replace(day=next_monday.day + 1)

    response = (f"📅 Информация о неделе:\n\n"
                f"Следующая неделя ({next_monday.strftime('%d.%m.%Y')}) - <b>{week_type}</b>")
    bot.send_message(message.chat.id, response, parse_mode="HTML")


def handle_ai_query(message):
    """Обработка запросов к ИИ."""
    bot.send_chat_action(message.chat.id, 'typing')
    response = generate_response(
        message.text,
        "Ты полезный помощник-бот для студентов ВГУ. Отвечай вежливо и информативно."
    )
    if response:
        bot.send_message(message.chat.id, response)
    else:
        bot.send_message(
            message.chat.id,
            "Произошла ошибка при обработке запроса. Попробуйте позже."
        )
    send_main_menu(message.chat.id)


def handle_clear_chat(message):
    """Очистка чата с подтверждением."""
    markup = types.InlineKeyboardMarkup()
    confirm_button = types.InlineKeyboardButton(
        text="✅ Да, очистить",
        callback_data="confirm_clear"
    )
    cancel_button = types.InlineKeyboardButton(
        text="❌ Нет, отменить",
        callback_data="cancel_clear"
    )
    markup.add(confirm_button, cancel_button)

    bot.send_message(
        message.chat.id,
        "Вы уверены, что хотите очистить чат? Это действие нельзя отменить.",
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: call.data in ['confirm_clear', 'cancel_clear'])
def clear_chat_confirmation(call):
    """Обработка подтверждения очистки чата."""
    if call.data == 'confirm_clear':
        try:
            # Удаляем сообщение с кнопками
            bot.delete_message(call.message.chat.id, call.message.message_id)

            # Отправляем сообщение о начале очистки
            msg = bot.send_message(call.message.chat.id, "⏳ Идет очистка чата...")

            # Получаем ID последнего сообщения
            last_id = msg.message_id

            # Удаляем сообщения бота (максимум 100 последних)
            for i in range(last_id, max(0, last_id - 100), -1):
                try:
                    bot.delete_message(call.message.chat.id, i)
                except:
                    continue

            bot.send_message(
                call.message.chat.id,
                "✅ Чат успешно очищен.",
                reply_markup=create_main_menu()
            )
        except Exception as e:
            logging.error(f"Ошибка при очистке чата: {e}")
            bot.send_message(
                call.message.chat.id,
                "❌ Не удалось полностью очистить чат."
            )
    else:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(
            call.message.chat.id,
            "Очистка чата отменена.",
            reply_markup=create_main_menu()
        )


def create_main_menu():
    """Создает клавиатуру главного меню."""
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        '🏫 Корпуса ВГУ',
        '🧭 Аудитории главного корпуса',
        '📰 Новости факультета',
        '⚽ Спортивные команды',
        '🤖 Задать вопрос ИИ',
        '📅 Числитель/знаменатель',
        '🧹 Очистить чат'
    ]
    keyboard.add(*buttons)
    return keyboard


def send_weekly_notification():
    """Отправка уведомлений о типе недели."""
    week_type = get_week_type()
    next_monday = datetime.now().date()

    while next_monday.weekday() != 0:
        next_monday = next_monday.replace(day=next_monday.day + 1)

    message = (f"🔔 Напоминание о типе недели:\n\n"
               f"Следующая неделя ({next_monday.strftime('%d.%m.%Y')}) - <b>{week_type}</b>")

    for user_id in user_states.keys():
        try:
            bot.send_message(user_id, message, parse_mode="HTML")
        except Exception as e:
            logging.error(f"Не удалось отправить уведомление пользователю {user_id}: {e}")


def schedule_checker():
    """Проверка запланированных задач."""
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except Exception as e:
            logging.error(f"Ошибка в планировщике: {e}")
            time.sleep(10)


# Планируем задачу на каждую субботу в 18:00
schedule.every().saturday.at("18:00").do(send_weekly_notification)

# Запускаем планировщик в отдельном потоке
threading.Thread(target=schedule_checker, daemon=True).start()

if __name__ == "__main__":
    logging.info("Бот запущен")
    bot.infinity_polling()