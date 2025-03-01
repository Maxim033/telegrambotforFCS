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
    bot.send_message(message.chat.id, "Choose your language:", reply_markup=keyboard)


@bot.message_handler(func=lambda message: message.text in languages.keys())
def handle_language_choice(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    language_code = languages[message.text]
    set_user_language(user_id, language_code)
    if language_code == 'en':
        bot.send_message(message.chat.id, f"Hello, {user_name}! You have chosen English language.")
        send_english_menu(message.chat.id)
    elif language_code == 'ru':
        bot.send_message(message.chat.id, f"Здравствуйте, {user_name}! Вы выбрали русский язык.")
        send_russian_menu(message.chat.id)


def send_english_menu(chat_id):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    btn = types.InlineKeyboardButton(text='How to get to the classrooms of the main building', callback_data='btn')
    btn1 = types.InlineKeyboardButton(text='Location of VSU buildings', callback_data='btn1')
    btn2 = types.InlineKeyboardButton(text='Faculty news and events', callback_data='btn2')
    btn3 = types.InlineKeyboardButton(text='I want to know about the sports teams of VSU', callback_data='btn3')
    btn4 = types.InlineKeyboardButton(text='Ask Artificial Intelligence a question!', callback_data='ask_ai')
    keyboard.add(btn, btn1, btn2, btn3, btn4)
    bot.send_message(chat_id, "Answers to frequently asked questions:", reply_markup=keyboard)


def send_russian_menu(chat_id):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    btn = types.InlineKeyboardButton(text='Как добраться до аудиторий главного корпуса', callback_data='btn')
    btn1 = types.InlineKeyboardButton(text='Расположение корпусов ВГУ', callback_data='btn1')
    btn2 = types.InlineKeyboardButton(text='Новости и события факультета', callback_data='btn2')
    btn3 = types.InlineKeyboardButton(text='Хочу узнать о спортивных командах ВГУ', callback_data='btn3')
    btn4 = types.InlineKeyboardButton(text='Задайте вопрос Искусственному интеллекту!', callback_data='ask_ai')
    keyboard.add(btn, btn1, btn2, btn3, btn4)
    bot.send_message(chat_id, "Другие вопросы:", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_query_handler(call):
    user_id = call.from_user.id
    user_name = call.from_user.first_name
    language_code = get_user_language(user_id)

    if language_code == 'en':
        if call.data == 'btn':
            bot.send_message(call.message.chat.id, "You choose: How to get to the classrooms of the main building")
            bot.send_message(call.message.chat.id,
                             "You can find the way through the labyrinths of VSU here: https://drive.google.com/file/d/1FFqGDxrR2L-E4Bpb-jybSCw2kyX9tQJy/view?usp=sharing\nAnd the first digit of the room number corresponds to the floor where it is located.")
        elif call.data == 'btn1':
            bot.send_message(call.message.chat.id, "You choose: location of VSU buildings")
            bot.send_message(call.message.chat.id,
                             "Here are the numbers and addresses of the buildings where classes or exams can be held: Main Building - University Square 1, Second Building - Lenina Street 10, Third Building - Revolution Avenue 24, Fifth Building - Hoolzunova Street 40, 5th Building - Hoolzunova Street 42b, Sixth Building - Hoolzunova Street 40a")
        elif call.data == 'btn2':
            bot.send_message(call.message.chat.id, "You choose: where can I find out about faculty news and events?")
            bot.send_message(call.message.chat.id,
                             "https://vk.com/fknabitur and https://vk.com/cs_vsu - here you can find all the important news of the faculty")
        elif call.data == 'btn3':
            bot.send_message(call.message.chat.id, "You choose: want to know about the sports teams of VSU")
            bot.send_message(call.message.chat.id,
                             "https://vk.com/bobry_vsu - here you can find out more about all the sports sections of VSU and find a community of the sport you are interested in")
        elif call.data == 'ask_ai':
            bot.send_message(call.message.chat.id,
                             "You choose: Didn't find an answer to your question? Ask the Artificial Intelligence!")
            bot.send_message(call.message.chat.id, "Please enter your question for the AI:")
            bot.register_next_step_handler(call.message, handle_ai_query)
    elif language_code == 'ru':
        if call.data == 'btn':
            bot.send_message(call.message.chat.id, "Вы выбрали: Как добраться до учебных аудиторий главного корпуса")
            bot.send_message(call.message.chat.id,
                             "Вы можете найти путь через лабиринты ВГУ здесь: https://drive.google.com/file/d/1FFqGDxrR2L-E4Bpb-jybSCw2kyX9tQJy/view?usp=sharing\nА первая цифра номера аудитории соответствует этажу, на котором она расположена.")
        elif call.data == 'btn1':
            bot.send_message(call.message.chat.id, "Вы выбрали: расположение корпусов ВГУ")
            bot.send_message(call.message.chat.id,
                             "Вот номера и адреса корпусов, где могут проходить занятия или экзамены: Главный корпус - Университетская площадь 1, Второй корпус - Ленина 10, Третий корпус - Революции 24, Пятый корпус - Улица Хоольцонова 40, Пятый корпус - Улица Хоольцонова 42б, Шестой корпус - Улица Хоольцонова 40а")
        elif call.data == 'btn2':
            bot.send_message(call.message.chat.id, "Вы выбрали: где узнать о новостях факультета и мероприятиях?")
            bot.send_message(call.message.chat.id,
                             "https://vk.com/fknabitur и https://vk.com/cs_vsu - здесь вы можете узнать все важные новости факультета")
        elif call.data == 'btn3':
            bot.send_message(call.message.chat.id, "Вы выбрали: хотите узнать о спортивных командах ВГУ")
            bot.send_message(call.message.chat.id,
                             "https://vk.com/bobry_vsu - здесь вы можете узнать больше о всех спортивных секциях ВГУ и найти сообщество, интересующее вас")
        elif call.data == 'ask_ai':
            bot.send_message(call.message.chat.id,
                             "Вы выбрали: Не нашли ответ на свой вопрос? Задайте вопрос искусственному интеллекту!")
            bot.send_message(call.message.chat.id, "Введите ваш вопрос для ИИ:")
            bot.register_next_step_handler(call.message, handle_ai_query)


def handle_ai_query(message):
    user_query = message.text
    try:
        response = generate_response(user_query, "You are a helpful assistant.")
        bot.send_message(message.chat.id, response, parse_mode="Markdown")
    except Exception as e:
        logging.error(f"Error: {e}")
        bot.send_message(message.chat.id,
                         "Произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте еще раз позже.")


def send_notification():
    now = datetime.now()
    if now.month == 9 and now.day >= 1 and now.day <= 7:
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


# Планируем задачу на каждую субботу в 18:00
schedule.every().saturday.at("18:00").do(send_notification)

# Запускаем планировщик в отдельном потоке
threading.Thread(target=schedule_checker, daemon=True).start()

if __name__ == "__main__":
    bot.polling(none_stop=True)