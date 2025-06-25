import os
import telebot
from telebot import types
import openai
import schedule
import time
import threading
from datetime import datetime
import logging

# Настройка логирования
logging.basicConfig(level=logging.ERROR)

# Загрузка ключей из переменных окружения
openai.api_key = os.getenv('OPENAI_API_KEY')
bot = telebot.TeleBot(os.getenv('TELEGRAM_BOT_TOKEN'))

languages = {
    'Русский': 'ru',
    'English': 'en'
}

user_states = {}

def get_user_language(user_id):
    return user_states.get(user_id, 'en')

def set_user_language(user_id, language_code):
    user_states[user_id] = language_code

def generate_response(user_query, context):
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

@bot.message_handler(commands=['start'])
def handle_start(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*languages.keys())
    bot.send_message(message.chat.id, "Choose your language / Выберите язык:", reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text in languages.keys())
def handle_language_choice(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    language_code = languages[message.text]
    set_user_language(user_id, language_code)
    if language_code == 'en':
        bot.send_message(message.chat.id, f"Hello, {user_name}! You have chosen English language.")
        send_english_menu(message.chat.id)
    else:
        bot.send_message(message.chat.id, f"Здравствуйте, {user_name}! Вы выбрали русский язык.")
        send_russian_menu(message.chat.id)

def send_english_menu(chat_id):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    btn = types.InlineKeyboardButton(text='How to get to the classrooms of the main building', callback_data='btn')
    btn1 = types.InlineKeyboardButton(text='Location of VSU buildings', callback_data='btn1')
    btn2 = types.InlineKeyboardButton(text='Faculty news and events', callback_data='btn2')
    btn3 = types.InlineKeyboardButton(text='I want to know about the sports teams of VSU', callback_data='btn3')
    btn4 = types.InlineKeyboardButton(text='Ask Artificial Intelligence a question!', callback_data='ask_ai')
    btn5 = types.InlineKeyboardButton(text='🎉 VSU Activities', callback_data='activities')
    btn6 = types.InlineKeyboardButton(text='🧹 Clear chat', callback_data='clear_chat')
    keyboard.add(btn, btn1, btn2, btn3, btn4, btn5, btn6)
    bot.send_message(chat_id, "Answers to frequently asked questions:", reply_markup=keyboard)

def send_russian_menu(chat_id):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    btn = types.InlineKeyboardButton(text='Как добраться до аудиторий главного корпуса', callback_data='btn')
    btn1 = types.InlineKeyboardButton(text='Расположение корпусов ВГУ', callback_data='btn1')
    btn2 = types.InlineKeyboardButton(text='Новости и события факультета', callback_data='btn2')
    btn3 = types.InlineKeyboardButton(text='Хочу узнать о спортивных командах ВГУ', callback_data='btn3')
    btn4 = types.InlineKeyboardButton(text='Задайте вопрос Искусственному интеллекту!', callback_data='ask_ai')
    btn5 = types.InlineKeyboardButton(text='🎉 Активности ВГУ', callback_data='activities')
    btn6 = types.InlineKeyboardButton(text='🧹 Очистить чат', callback_data='clear_chat')
    keyboard.add(btn, btn1, btn2, btn3, btn4, btn5, btn6)
    bot.send_message(chat_id, "Другие вопросы:", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def callback_query_handler(call):
    user_id = call.from_user.id
    language_code = get_user_language(user_id)

    def send_message(text):
        bot.send_message(call.message.chat.id, text)

    def send_activities():
        if language_code == 'en':
            text = (
                "🎉 VSU Activities:\n"
                "- Sports events\n"
                "- Cultural festivals\n"
                "- Scientific conferences\n"
                "- Volunteer projects\n"
                "More info on the university website."
            )
        else:
            text = (
                "🎉 Активности ВГУ:\n"
                "- Спортивные мероприятия\n"
                "- Культурные фестивали\n"
                "- Научные конференции\n"
                "- Волонтерские проекты\n"
                "Подробнее на сайте университета."
            )
        send_message(text)

    def clear_chat():
        try:
            chat_id = call.message.chat.id
            message_id = call.message.message_id
            for i in range(10):
                try:
                    bot.delete_message(chat_id, message_id - i)
                except Exception:
                    pass
            send_message("🧹 Chat cleared (bot messages only)." if language_code == 'en' else "🧹 Чат очищен (только сообщения бота).")
        except Exception as e:
            logging.error(f"Error clearing chat: {e}")
            send_message("⚠️ Unable to clear chat." if language_code == 'en' else "⚠️ Не удалось очистить чат.")

    if language_code == 'en':
        if call.data == 'btn':
            send_message("You choose: How to get to the classrooms of the main building\n"
                         "You can find the way through the labyrinths of VSU here: https://drive.google.com/file/d/1FFqGDxrR2L-E4Bpb-jybSCw2kyX9tQJy/view?usp=sharing\n"
                         "And the first digit of the room number corresponds to the floor where it is located.")
        elif call.data == 'btn1':
            send_message("You choose: location of VSU buildings\n"
                         "Main Building - University Square 1\n"
                         "Second Building - Lenina Street 10\n"
                         "Third Building - Revolution Avenue 24\n"
                         "Fifth Building - Hoolzunova Street 40\n"
                         "5th Building - Hoolzunova Street 42b\n"
                         "Sixth Building - Hoolzunova Street 40a")
        elif call.data == 'btn2':
            send_message("You choose: where can I find out about faculty news and events?\n"
                         "https://vk.com/fknabitur and https://vk.com/cs_vsu - here you can find all important faculty news")
        elif call.data == 'btn3':
            send_message("You choose: want to know about the sports teams of VSU\n"
                         "https://vk.com/bobry_vsu - here you can find info about all VSU sports sections and communities")
        elif call.data == 'ask_ai':
            sent = bot.send_message(call.message.chat.id, "Please enter your question for the AI:")
            bot.register_next_step_handler(sent, handle_ai_query)
        elif call.data == 'activities':
            send_activities()
        elif call.data == 'clear_chat':
            clear_chat()
        else:
            send_message("Unknown command.")
    else:  # русский
        if call.data == 'btn':
            send_message("Вы выбрали: Как добраться до учебных аудиторий главного корпуса\n"
                         "Вы можете найти путь через лабиринты ВГУ здесь: https://drive.google.com/file/d/1FFqGDxrR2L-E4Bpb-jybSCw2kyX9tQJy/view?usp=sharing\n"
                         "А первая цифра номера аудитории соответствует этажу, на котором она расположена.")
        elif call.data == 'btn1':
            send_message("Вы выбрали: расположение корпусов ВГУ\n"
                         "Главный корпус - Университетская площадь 1\n"
                         "Второй корпус - Ленина 10\n"
                         "Третий корпус - Революции 24\n"
                         "Пятый корпус - Улица Хоольцонова 40\n"
                         "Пятый корпус - Улица Хоольцонова 42б\n"
                         "Шестой корпус - Улица Хоольцонова 40а")
        elif call.data == 'btn2':
            send_message("Вы выбрали: где узнать о новостях факультета и мероприятиях?\n"
                         "https://vk.com/fknabitur и https://vk.com/cs_vsu - здесь вы можете узнать все важные новости факультета")
        elif call.data == 'btn3':
            send_message("Вы выбрали: хотите узнать о спортивных командах ВГУ\n"
                         "https://vk.com/bobry_vsu - здесь вы можете узнать больше о спортивных секциях ВГУ и найти интересующее сообщество")
        elif call.data == 'ask_ai':
            sent = bot.send_message(call.message.chat.id, "Введите ваш вопрос для ИИ:")
            bot.register_next_step_handler(sent, handle_ai_query)
        elif call.data == 'activities':
            send_activities()
        elif call.data == 'clear_chat':
            clear_chat()
        else:
            send_message("Неизвестная команда.")

def handle_ai_query(message):
    user_query = message.text
    try:
        response = generate_response(user_query, "You are a helpful assistant.")
        bot.send_message(message.chat.id, response, parse_mode="Markdown")
    except Exception as e:
        logging.error(f"Error: {e}")
        if get_user_language(message.from_user.id) == 'en':
            bot.send_message(message.chat.id,
                             "An error occurred while processing your request. Please try again later.")
        else:
            bot.send_message(message.chat.id,
                             "Произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте еще раз позже.")

def send_notification():
    now = datetime.now()
    # Пример логики для числитель/знаменатель
    if now.month == 9 and 1 <= now.day <= 7:
        week_type = "числитель"
    else:
        week_number = now.isocalendar()[1]
        week_type = "числитель" if week_number % 2 == 1 else "знаменатель"

    message = f"На следующей неделе ({now.strftime('%d.%m.%Y')}) будет {week_type}."
    for user_id in user_states.keys():
        try:
            bot.send_message(user_id, message)
        except Exception as e:
            logging.error(f"Error sending notification to user {user_id}: {e}")

def schedule_checker():
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except Exception as e:
            logging.error(f"Error in schedule checker: {e}")
            time.sleep(10)

# Запускаем планировщик на каждую субботу 18:00
schedule.every().saturday.at("18:00").do(send_notification)
threading.Thread(target=schedule_checker, daemon=True).start()

if __name__ == "__main__":
    bot.polling(none_stop=True)
