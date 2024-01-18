import telebot
from telebot import types
import datetime
from db import init_db, get_feedbacks, save_feedback, get_feedbacks_by_date

# проверка наличия бд
init_db()

token = '6408738573:AAGsSAosjsqsXvlM_6JIzKKDP-LLaekGi2E'
bot = telebot.TeleBot(token)

ADMIN_USER_ID = 423672005

@bot.message_handler(commands=['get_feedback'])
def handle_get_feedback(message):
    if message.from_user.id == ADMIN_USER_ID:
        feedbacks = get_feedbacks()
        response = "Список всех отзывов:\n\n"
        for feedback in feedbacks:
            response += f"ID: {feedback[0]}\nUser ID: {feedback[1]}\nFeedback: {feedback[2]}\n\n"
        bot.send_message(message.chat.id, response)
    else:
        bot.send_message(message.chat.id, 'У вас нет доступа к этой команде.')

def process_save_feedback(message):
    feedback_text = message.text
    user_id = message.from_user.id
    created_at = datetime.datetime.now().strftime('%Y-%m-%d')
    bot.send_message(message.chat.id, 'Спасибо за ваш отзыв!', reply_markup=types.ReplyKeyboardRemove())
@bot.message_handler(commands=['get_feedback_by_date'])
def handle_get_feedback_by_date(message):
    if message.from_user.id == ADMIN_USER_ID:
        msg = bot.send_message(message.chat.id, 'Введите дату для получения отзывов в формате ГГГГ-ММ-ДД:')
        bot.register_next_step_handler(msg, show_feedbacks_by_date)
    else:
        bot.send_message(message.chat.id, 'У вас нет доступа к этой команде.')

def show_feedbacks_by_date(message):
    date = message.text
    try:
        datetime.datetime.strptime(date, '%Y-%m-%d')  # проверка даты
    except ValueError:
        bot.send_message(message.chat.id, 'Неправильный формат даты. Используйте ГГГГ-ММ-ДД.')
        return

    feedbacks = get_feedbacks_by_date(date)
    if feedbacks:
        response = f"Отзывы за дату {date}:\n\n"
        for feedback in feedbacks:
            response += f"ID: {feedback[0]}\nUser ID: {feedback[1]}\nFeedback: {feedback[2]}\nДата: {feedback[3]}\n\n"
    else:
        response = f"Отзывы за дату {date} не найдены."
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