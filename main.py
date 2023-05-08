"""
Дипломний проєкт Усачика Дениса КБ-19-1
Тема: Чат-бот для споживачів відеоіндустрії
Назва бота: CineBot
Посилання на бота: https://t.me/cine_rec_bot
"""


# бібліотеки з токенами, стікерами, а також з окремим функціями ШІ
import config
import ai
import stickers
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

# під'єднуємось до бази даних, якщо база даних існує то вказати шлях до неї
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
    markup = types.ReplyKeyboardMarkup(resize_keyboard = True, row_width = 3)
    # створюємо кнопки для клавіатури
    item1 = types.KeyboardButton('➕ Додати запис')
    item2 = types.KeyboardButton('📄 Показати записи')
    item3 = types.KeyboardButton('❌ Очистити список')
    item4 = types.KeyboardButton('🎬 Топ-100 фільмів')
    item5 = types.KeyboardButton('🎲 Рандомний фільм')
    item6 = types.KeyboardButton('🎞 Схожий фільм')
    item7 = types.KeyboardButton('🎭 Добірка за жанром')
    # додаємо кнопки до клавіатури
    markup.add(item1, item2, item3, item4, item7, item6, item5)
    # виводимо вітальне повідомлення
    bot.send_sticker(message.chat.id, stickers.sticker_hi)
    bot.send_message(message.chat.id, "Привіт, <b>{0.first_name}</b>! 👋\nЯ ваш персональний помічник у світі кіно - <b>CіneBot</b>.\nЧим саме я можу допомогти?\n\n<i>(Оберіть один з варіантів на клавіатурі)</i>".format(message.from_user), parse_mode='html', reply_markup = markup)
    
# обробка клавіатури"
@bot.message_handler(content_types=['text'])
def menu(message):
    #якщо це приватне повідомлення
    if message.chat.type == 'private':
        #якщо це кнопка "додати запис"
        if message.text == '➕ Додати запис':
            bot.send_sticker(message.chat.id, stickers.sticker_type)
            msg = bot.send_message(message.chat.id, 'Надішліть мені назву фільма, я її запишу!')
            # очікує текст від користувача та визиває функцію adddb яка зберігає в БД
            bot.register_next_step_handler(msg,adddb)
        #якщо це кнопка "показати запис"

        elif message.text == '📄 Показати записи':
            user_id = message.from_user.id
            # вибірка даних з бази даних для даного користувача
            cursor.execute(f"SELECT message FROM messages WHERE user_id = {user_id}")
            results = cursor.fetchall()
            # відправлення результатів користувачу
            if results:
                message_text = "\n".join([result[0] for result in results])
                bot.send_sticker(message.chat.id, stickers.sticker_hug)
                bot.send_message(message.chat.id, f"Ваш список збережений фільмів:\n\n{message_text}")
            else:
                bot.send_sticker(message.chat.id, stickers.sticker_question)
                bot.send_message(message.chat.id, 'У Вас поки немає записаних фільмів.')
        #якщо це кнопка "очистити записи"

        elif message.text == '❌ Очистити список':
            # видаляє дані для конкретного користувача
            cursor.execute(f"DELETE FROM messages WHERE user_id = {message.from_user.id}")
            conn.commit()
            bot.send_sticker(message.chat.id, stickers.sticker_yes)
            bot.send_message(message.chat.id, "Ваші записи були очищені! ✅")
        #якщо це кнопка "топ 100"

        elif message.text == '🎬 Топ-100 фільмів':
            # отримуємо топ 250 фільмів
            top_movies = ia.get_top250_movies()
            # формування тексту повідомлення
            text = "Топ-100 фільмів за версією IMDb:\n\n"
            for i in range(100):
                text += f"{i+1}. {top_movies[i]['title']} ({top_movies[i]['year']})\n"
            # відправлення повідомлення з топ-100 фільмів
            bot.send_sticker(message.chat.id, stickers.sticker_ride)
            bot.send_message(message.chat.id, text)
        # якщо це кнопка "рандомний фільм"

        elif message.text == '🎲 Рандомний фільм':
            top_movies = ia.get_top250_movies()
            # повертаємо 1 фідбм з вибірки у 100 фільмів
            random_movie = ia.get_movie(top_movies[random.randint(0, 99)].getID())
            # формування тексту повідомлення
            title = random_movie['title']
            year = random_movie['year']
            genres = ', '.join(random_movie['genres'])
            directors = ', '.join([director['name'] for director in random_movie['directors']])
            response = f'{title} ({year})\n\n'
            response += f'Жанр(и): {genres}\n'
            response += f'Режисер(и): {directors}\n'
            imdb_id = random_movie.getID()
            # створюємо інлайн кнопку для переходу до фільму
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("Відкрити на IMDb", url=f"https://www.imdb.com/title/tt{imdb_id}/"))
            bot.send_sticker(message.chat.id, stickers.sticker_fun)
            bot.send_message(message.chat.id, "Ваш випадковий фільм:")
            bot.send_message(message.chat.id, response, reply_markup = markup)
        # якщо це кнопка "схожий фільм"

        elif message.text == '🎞 Схожий фільм':
            # просить вести назву фільму для пошуку
            bot.send_sticker(message.chat.id, stickers.sticker_type)
            msg = bot.send_message(message.chat.id, 'Введіть назву фільму, щоб отримати добірку фільмів схожих на нього')
            # визиває функцію з файлу ai
            bot.register_next_step_handler(msg,ai.AiRec.rec_name)
        
        elif message.text == '🎭 Добірка за жанром':
            # просить вести назву фільму для пошуку
            bot.send_sticker(message.chat.id, stickers.sticker_type)
            msg = bot.send_message(message.chat.id, 'Введіть жанр за яким хочете отримати добірку')
            # визиває функцію з файлу ai
            bot.register_next_step_handler(msg,ai.AiRec.rec_genre)

        else:
            oops = "Вибачте, я не знаю таку команду :("
            bot.send_sticker(message.chat.id, stickers.sticker_question)
            bot.send_message(message.chat.id, oops)

# функція яка додає дані до БД
def adddb(message):
    user_id = message.from_user.id
    message_text = message.text
    # Додавання даних до бази даних
    cursor.execute(f"INSERT INTO messages (user_id, message) VALUES ({user_id}, '{message_text}')")
    conn.commit()
    bot.send_sticker(message.chat.id, stickers.sticker_fun)
    bot.reply_to(message, 'Я записав ваш фільм! ✅')

# запуск бота
bot.polling(none_stop = True)