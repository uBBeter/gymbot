import telebot
from telebot import types
import sqlite3 as sq
import subprocess

API_KEY = "6482778607:AAFWJGa6qJOhhW8VJBvNuPOZdHAoXypxn5I"
bot = telebot.TeleBot(API_KEY)

@bot.message_handler(commands=['start'])
def start(message):
    with sq.connect('botdata.db') as conn:
        cur = conn.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_telegram_id TEXT,
        age INTEGER NOT NULL DEFAULT 20,
        sex TEXT NOT NULL DEFAULT "Мужской",
        current_weight INTEGER NOT NULL DEFAULT 0,
        wanted_weight INTEGER NOT NULL DEFAULT 0,
        role TEXT NOT NULL DEFAULT "user"
        )
        """)
        conn.commit()
        cur.execute(f'SELECT * FROM users WHERE user_telegram_id == {message.from_user.id}')
        result = cur.fetchone()
        if result:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            button_confirm = types.KeyboardButton("Да, я хочу изменить информацию о себе")
            button_reject = types.KeyboardButton("Нет")
            markup.add(button_confirm, button_reject)
            bot.send_message(message.chat.id, "Похоже, ты уже зарегестрирован. Ты хочешь зарегестрироваться заново?", reply_markup=markup)
            bot.register_next_step_handler(message, change_info)
        cur.close()
    bot.send_message(message.chat.id, "Привет! Расскажи мне о себе, а я помогу тебе составить диету :)")
    bot.send_message(message.chat.id, "Начнем с твоего возраста, сколько тебе лет?")
    bot.register_next_step_handler(message, user_age)

def change_info(message):
    message_text = message.text.strip()
    try:
        assert message_text == "Да, я хочу изменить информацию о себе" or message_text == "Нет"
    except AssertionError:
        bot.send_message(message.chat.id, "Пожалуйста, воспользуйся кнопками")
        bot.register_next_step_handler(message, change_info)
        return
    if message_text == "Да, я хочу изменить информацию о себе":
        with sq.connect('botdata.db') as conn:
            cur = conn.cursor()
            cur.execute(f'DELETE FROM users WHERE user_telegram_id == {message.from_user.id}')
            conn.commit()
            cur.close()
        markup = types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, "Хорошо, начнем с твоего возраста, сколько тебе лет?", reply_markup=markup)
        bot.register_next_step_handler(message, user_age)
    if message_text == "Нет":
        # TODO: when the clients panel is ready make a return to clients panel stage
        pass

def user_age(message):
    message_text = message.text.strip()
    try:
        age = int(message_text)
    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, введи возраст цифрами")
        bot.register_next_step_handler(message, user_age)
        return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_male = types.KeyboardButton("Мужской")
    button_female = types.KeyboardButton("Женский")
    markup.add(button_male, button_female)
    bot.send_message(message.chat.id, "Укажи свой пол", reply_markup=markup)
    bot.register_next_step_handler(message, user_sex, age)


def user_sex(message, age):
    message_text = message.text.strip()
    try:
        assert message_text == "Мужской" or message_text == "Женский"
    except AssertionError:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_male = types.KeyboardButton("Мужской")
        button_female = types.KeyboardButton("Женский")
        markup.add(button_male, button_female)
        bot.send_message(message.chat.id, "Пожалуйста, воспользуйся кнопками", reply_markup=markup)
        bot.register_next_step_handler(message, user_sex, age)
        return
    sex = message_text
    markup = types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, "Укажи свой текущий вес в килограмах", reply_markup=markup)
    bot.register_next_step_handler(message, user_current_weight, age, sex)


def user_current_weight(message, age, sex):
    message_text = message.text.strip()
    try:
        current_weight = int(message_text)
    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, укажи свой вес целым числом")
        bot.register_next_step_handler(message, user_current_weight, age, sex)
        return
    bot.send_message(message.chat.id, "Укажи свой желаемый вес в килограмах")
    bot.register_next_step_handler(message, user_wanted_weight, age, sex, current_weight)



def user_wanted_weight(message, age, sex, current_weight):
    message_text = message.text.strip()
    try:
        wanted_weight = int(message_text)
    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, укажи желаемый вес целым числом")
        bot.register_next_step_handler(message, user_wanted_weight, age, sex, current_weight)  
        return    
    bot.send_message(message.chat.id, "Отлично, давай проверим, все ли правильно")
    bot.send_message(message.chat.id, f"Твой возраст: {age}\nТвой пол: {sex}\nТвой текущий вес: {current_weight}\nТвой желаемый вес: {wanted_weight}")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_confirm = types.KeyboardButton("Да, всё верно")
    button_restart = types.KeyboardButton("Начать заново")
    markup.add(button_confirm, button_restart)
    bot.send_message(message.chat.id, "Всё верно?", reply_markup=markup)
    bot.register_next_step_handler(message, confirmation, age, sex, current_weight, wanted_weight)


def confirmation(message, age, sex, current_weight, wanted_weight):
    message_text = message.text.strip()
    try:
        assert message_text == "Да, всё верно" or message_text == "Начать заново"
    except AssertionError:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_confirm = types.KeyboardButton("Да, всё верно")
        button_restart = types.KeyboardButton("Начать заново")
        markup.add(button_confirm, button_restart)
        bot.send_message(message.chat.id, "Пожалуйста, воспользуйся кнопками", reply_markup=markup)
        bot.register_next_step_handler(message, confirmation, age, sex, current_weight, wanted_weight)
        return
    markup = types.ReplyKeyboardRemove()
    if message_text == "Да, всё верно":
        bot.send_message(message.chat.id, "Отлично, сейчас составлю тебе диету", reply_markup=markup)
        id = message.from_user.id
        with sq.connect("botdata.db") as conn:
            cur = conn.cursor()
            cur.execute(f'INSERT INTO users (user_telegram_id, age, sex, current_weight, wanted_weight) VALUES ("{id}", "{age}", "{sex}", "{current_weight}", "{wanted_weight}")')
            conn.commit()
            cur.close()
    elif message_text == "Начать заново":
        bot.send_message(message.chat.id, "Начнем с твоего возраста, сколько тебе лет?", reply_markup=markup)
        bot.register_next_step_handler(message, user_age)


@bot.message_handler(commands=['admin_panel'])
def check_if_admin(message):
    with sq.connect('botdata.db') as conn:
        cur = conn.cursor()
        cur.execute(f'SELECT role FROM users WHERE user_telegram_id == {message.from_user.id}')
        role = cur.fetchone()
        cur.close()
        if role:
            role = role[0]
    try:
        assert role == 'admin'
    except AssertionError:
        bot.send_message(message.chat.id, "Доступ запрещен")
        return
    bot.send_message(message.chat.id, "Доступ разрешен")


bot.polling(non_stop=True)