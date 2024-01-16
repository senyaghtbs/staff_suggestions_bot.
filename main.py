import sqlite3
import telebot
from telebot import types

# создаем бд
conn = sqlite3.connect('feedback.db', check_same_thread=False) # Разрешить доступ из разных потоков
cursor = conn.cursor()

# таблица отзывов
cursor.execute('''CREATE TABLE IF NOT EXISTS feedbacks
               (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, feedback TEXT)''')
conn.commit()

token = '6408738573:AAGsSAosjsqsXvlM_6JIzKKDP-LLaekGi2E'
bot = telebot.TeleBot(token)

ADMIN_USER_ID = 423672005

@bot.message_handler(commands=['get_feedback'])
def get_feedback(message):
    if message.from_user.id == ADMIN_USER_ID:
        with sqlite3.connect('feedback.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM feedbacks')
            feedbacks = cursor.fetchall()
            response = "Список всех отзывов:\n\n"
            for feedback in feedbacks:
                response += f"ID: {feedback[0]}\nUser ID: {feedback[1]}\nFeedback: {feedback[2]}\n\n"
            bot.send_message(message.chat.id, response)
    else:
        bot.send_message(message.chat.id, 'У вас нет доступа к этой команде.')

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Привет, напиши /help, чтобы увидеть все команды и пояснения')

@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.chat.id, 'Нажмите на кнопку отправить отзыв /reply')

@bot.message_handler(commands=['reply'])
def button(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    items1 = types.KeyboardButton('Оставить свой отзыв')
    markup.add(items1)
    msg = bot.send_message(message.chat.id, 'Какой отзыв вы хотите отправить?', reply_markup=markup)
    bot.register_next_step_handler(msg, process_feedback_step)

def process_feedback_step(message):
    if message.text == 'Оставить свой отзыв':
        msg = bot.send_message(message.chat.id, 'Пожалуйста, напишите ваш отзыв:')
        bot.register_next_step_handler(msg, save_feedback)
    else:
        bot.send_message(message.chat.id, 'Отмена действия.', reply_markup=types.ReplyKeyboardRemove())

def save_feedback(message):
    feedback = message.text
    user_id = message.from_user.id
    # записываем отзыв в бд
    with sqlite3.connect('feedback.db') as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO feedbacks (user_id, feedback) VALUES (?, ?)', (user_id, feedback))
        conn.commit()
    bot.send_message(message.chat.id, 'Спасибо за ваш отзыв!', reply_markup=types.ReplyKeyboardRemove())

bot.infinity_polling()