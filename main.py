import sqlite3
import telebot
from telebot import types
import datetime

# создаем бд
conn = sqlite3.connect('feedback.db', check_same_thread=False)
cursor = conn.cursor()

# таблица отзывов
cursor.execute('''CREATE TABLE IF NOT EXISTS feedbacks
               (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, feedback TEXT)''')
conn.commit()

#провелка на наличия таблицы
cursor.execute("PRAGMA table_info(feedbacks)")
columns = [info[1] for info in cursor.fetchall()]  # Получаем список названий колонок
if 'created_at' not in columns:
    cursor.execute('ALTER TABLE feedbacks ADD COLUMN created_at DATE')
    conn.commit()

# Закрываем соединение с БД
cursor.close()
conn.close()

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


def save_feedback(message):
    feedback = message.text
    user_id = message.from_user.id
    created_at = datetime.datetime.now().strftime('%Y-%m-%d') # Форматируем текущую дату
    # записываем отзыв в бд
    with sqlite3.connect('feedback.db') as conn:
        cursor = conn.cursor()
        # Обратите внимание на добавленный столбец created_at
        cursor.execute('INSERT INTO feedbacks (user_id, feedback, created_at) VALUES (?, ?, ?)', (user_id, feedback, created_at))
        conn.commit()
    bot.send_message(message.chat.id, 'Спасибо за ваш отзыв!', reply_markup=types.ReplyKeyboardRemove())


@bot.message_handler(commands=['get_feedback_by_date'])
def get_feedback_by_date(message):
    if message.from_user.id == ADMIN_USER_ID:
        msg = bot.send_message(message.chat.id, 'Введите дату для получения отзывов в формате ГГГГ-ММ-ДД:')
        bot.register_next_step_handler(msg, show_feedbacks_by_date)
    else:
        bot.send_message(message.chat.id, 'У вас нет доступа к этой команде.')

def show_feedbacks_by_date(message):
    date = message.text
    try:
        # Проверка правильности формата даты
        datetime.datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        bot.send_message(message.chat.id, 'Неправильный формат даты. Используйте ГГГГ-ММ-ДД.')
        return

    with sqlite3.connect('feedback.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM feedbacks WHERE created_at = ?', (date,))
        feedbacks = cursor.fetchall()
        if feedbacks:
            response = "Отзывы за дату {}:\n\n".format(date)
            for feedback in feedbacks:
                response += f"ID: {feedback[0]}\nUser ID: {feedback[1]}\nFeedback: {feedback[2]}\nДата: {feedback[3]}\n\n"
        else:
            response = "Отзывы за дату {} не найдены.".format(date)
        bot.send_message(message.chat.id, response)

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Привет, напиши /help, чтобы увидеть все команды и пояснения')

@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.chat.id, 'Отправить отзыв: /reply\n'
                                      'Получить отзыв: /get_feedback\n'
                      'Получить отзыв по дате: /get_feedback_by_date\n')

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



bot.infinity_polling()