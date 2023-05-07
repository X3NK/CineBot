import telebot
import config
import openai

openai.api_key = (config.AIkey)
bot = telebot.TeleBot(config.TOKEN)

class Rec:
    def airec(message):
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=f"Виведи мені фільми схожі на: {message.text}, виведи тільки пронумерований список фільмів з назвою на анлійській мові та з роком виходу",
            temperature=0,
            max_tokens=1000,
            top_p=1.0,
            frequency_penalty=0.5,
            presence_penalty=0.0,
        )
        bot.send_message(message.chat.id, text=response['choices'][0]['text'])