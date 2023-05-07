"""
Дипломний проєкт Усачика Дениса КБ-19-1
Тема: Чат-бот для споживачів відеоіндустрії
Назва бота: CineBot
Посилання на бота: https://t.me/cine_rec_bot
"""


# бібліотеки з токенами, а також з окремим функціями ШІ
import config
import ai
# імпортуємо бібліотеки
import telebot
import sqlite3
import random
import openai
import imdb
from imdb import IMDb
from telebot import types

# токен телеграм бота
bot = telebot.TeleBot(config.TOKEN)

# створення об'єкту IMDb
ia = IMDb()

# під'єднуємось до бази даних
conn = sqlite3.connect('C:\\Users\\usach\\Desktop\\CineBot\\database.db', check_same_thread=False)
# створюємо курсор
cursor = conn.cursor()
# створюємо таблицю якщо її не існує
cursor.execute('''CREATE TABLE IF NOT EXISTS messages
                (user_id INTEGER, message TEXT)''')
conn.commit()

# обробка команди /старт
@bot.message_handler(commands=['start'])
def start(message):
    # створюємо клавіатуру
    markup = types.ReplyKeyboardMarkup(resize_keyboard = True)
    # створюємо кнопки для клавіатури
    item1 = types.KeyboardButton('➕ Додати запис')
    item2 = types.KeyboardButton('📄 Показати записи')
    item3 = types.KeyboardButton('❌ Очистити список')
    item4 = types.KeyboardButton('🎬 Топ-100 фільмів')
    item5 = types.KeyboardButton('🎲 Рандомний фільм')
    item6 = types.KeyboardButton('🎞 Схожий фільм')
    # додаємо кнопки до клавіатури
    markup.add(item1, item2, item3, item4, item5, item6)
    # виводимо вітальне повідомлення
    bot.send_message(message.chat.id, "Привіт, <b>{0.first_name}</b>!".format(message.from_user), parse_mode='html', reply_markup = markup)

# обробка клавіатури"
@bot.message_handler(content_types=['text'])
def menu(message):
    #якщо це приватне повідомлення
    if message.chat.type == 'private':
        #якщо це кнопка "додати запис"
        if message.text == '➕ Додати запис':
            msg = bot.send_message(message.chat.id, 'Надішліть мені назву фільма і я її запишу!')
            # очікує текст від користувача та визиває функцію adddb яка зберігає в БД
            bot.register_next_step_handler(msg,adddb)
        #якщо це кнопка "показати запис"

        if message.text == '📄 Показати записи':
            user_id = message.from_user.id
            # вибірка даних з бази даних для даного користувача
            cursor.execute(f"SELECT message FROM messages WHERE user_id = {user_id}")
            results = cursor.fetchall()
            # відправлення результатів користувачу
            if results:
                message_text = "\n".join([result[0] for result in results])
                bot.reply_to(message, message_text)
            else:
                bot.reply_to(message, 'У Вас поки немає записаних фільмів!')
        #якщо це кнопка "очистити записи"

        if message.text == '❌ Очистити список':
            # видаляє дані для конкретного користувача
            cursor.execute(f"DELETE FROM messages WHERE user_id = {message.from_user.id}")
            conn.commit()
            bot.reply_to(message, "Ваші записи були очищені!")
        #якщо це кнопка "топ 100"

        if message.text == '🎬 Топ-100 фільмів':
            # отримуємо топ 250 фільмів
            top_movies = ia.get_top250_movies()
            # формування тексту повідомлення
            text = "Топ-100 фільмів за версією IMDb:\n\n"
            for i in range(100):
                text += f"{i+1}. {top_movies[i]['title']} ({top_movies[i]['year']})\n"
            # відправлення повідомлення з топ-100 фільмів
            bot.send_message(message.chat.id, text)
        # якщо це кнопка "рандомний фільм"

        if message.text == '🎲 Рандомний фільм':
            top_movies = ia.get_top250_movies()
            # повертаємо 1 фідбм з вибірки у 100 фільмів
            random_movie = ia.get_movie(top_movies[random.randint(0, 99)].getID())
            # формування тексту повідомлення
            title = random_movie['title']
            year = random_movie['year']
            genres = ', '.join(random_movie['genres'])
            directors = ', '.join([director['name'] for director in random_movie['directors']])
            response = f'{title} ({year})\n\n'
            response += f'Жанр: {genres}\n'
            response += f'Режисер(и): {directors}\n'
            imdb_id = random_movie.getID()
            # створюємо інлайн кнопку для переходу до фільму
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("Відкрити на IMDb", url=f"https://www.imdb.com/title/tt{imdb_id}/"))
            bot.send_message(message.chat.id, response, reply_markup = markup)
        # якщо це кнопка "схожий фільм"

        if message.text == '🎞 Схожий фільм':
            # просить вести назву фільму для пошуку
            msg = bot.send_message(message.chat.id, 'Введіть назву фільму, щоб отримати підбірку з схожими на нього')
            # визиває функцію з файлу ai
            bot.register_next_step_handler(msg,ai.Rec.airec)

# функція яка додає дані до БД
def adddb(message):
    user_id = message.from_user.id
    message_text = message.text
    # Додавання даних до бази даних
    cursor.execute(f"INSERT INTO messages (user_id, message) VALUES ({user_id}, '{message_text}')")
    conn.commit()
    bot.reply_to(message, 'Я записав Ваш фільм!')

# запуск бота
bot.polling(none_stop = True)