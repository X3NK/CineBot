import telebot
import config
import openai
import stickers

openai.api_key = (config.AIkey)
bot = telebot.TeleBot(config.TOKEN)

class AiRec:
    def check_and_remove_prefix(variable):
        if variable.startswith("."):
            variable = variable[2:]
        return variable
    
    def rec_name(message):
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=f"Виведи мені добірку фільмів схожих на: {message.text}, виведи тільки пронумерований список фільмів з назвою на анлійській мові та з роком виходу",
            temperature=0,
            max_tokens=1000,
            top_p=1.0,
            frequency_penalty=0.5,
            presence_penalty=0.0,
        )
        text=response['choices'][0]['text']
        text = AiRec.check_and_remove_prefix(text)
        bot.send_sticker(message.chat.id, stickers.sticker_fun)
        bot.send_message(message.chat.id, f"Ось ваша добірка за схожим фільмом:\n{text}")

    def rec_genre(message):
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=f"Виведи мені добірку фільмів за жанром: {message.text}, виведи тільки пронумерований список фільмів з назвою на анлійській мові та з роком виходу",
            temperature=0,
            max_tokens=1000,
            top_p=1.0,
            frequency_penalty=0.5,
            presence_penalty=0.0,
        )
        text=response['choices'][0]['text']
        text = AiRec.check_and_remove_prefix(text)
        bot.send_sticker(message.chat.id, stickers.sticker_fun)
        bot.send_message(message.chat.id, f"Ось ваша добірка за жанрами:\n{text}")