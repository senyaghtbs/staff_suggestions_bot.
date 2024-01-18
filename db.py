import sqlite3

# создаем бд
conn = sqlite3.connect('feedback.db', check_same_thread=False)
cursor = conn.cursor()

#таблица отзывов
cursor.execute('''CREATE TABLE IF NOT EXISTS feedbacks
               (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, feedback TEXT)''')
conn.commit()

#провелка на наличия таблицы
cursor.execute("PRAGMA table_info(feedbacks)")
columns = [info[1] for info in cursor.fetchall()]  #колонки
if 'created_at' not in columns:
    cursor.execute('ALTER TABLE feedbacks ADD COLUMN created_at DATE')
    conn.commit()
#закрыть бд
cursor.close()
conn.close()

def init_db():
    conn = sqlite3.connect('feedback.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS feedbacks
                   (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, feedback TEXT)''')
    conn.commit()
    cursor.execute("PRAGMA table_info(feedbacks)")
    columns = [info[1] for info in cursor.fetchall()]
    if 'created_at' not in columns:
        cursor.execute('ALTER TABLE feedbacks ADD COLUMN created_at DATE')
        conn.commit()
    cursor.close()
    conn.close()

def get_feedbacks():
    with sqlite3.connect('feedback.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM feedbacks')
        feedbacks = cursor.fetchall()
    return feedbacks


def save_feedback(user_id, feedback, created_at):
    with sqlite3.connect('feedback.db') as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO feedbacks (user_id, feedback, created_at) VALUES (?, ?, ?)', (user_id, feedback, created_at))
        conn.commit()

def get_feedbacks_by_date(date):
    with sqlite3.connect('feedback.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM feedbacks WHERE created_at = ?', (date,))
        feedbacks = cursor.fetchall()
    return feedbacks