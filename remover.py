import telebot
import json

file = open('token.json')
data = json.load(file)
bot = telebot.TeleBot(data['token'])
chat_id = '-1002137811828'

ids = [k for k in range(3000, 3158)]

for i in ids:
    bot.delete_messages_history(chat_id, i)


bot.polling(none_stop=True, interval=0)
