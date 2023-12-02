import telebot
from telebot import types
import os
import json
import glob
import time

def listfiles(folder):
    for root, folders, files in os.walk(folder):
        for filename in folders + files:
            yield os.path.join(root, filename)

file = open('token.json')
data = json.load(file)
bot = telebot.TeleBot(data['token'])
chat_id = '-1002137811828'

files =[]

def listallfiles(startpath):
    for filename in os.listdir(startpath):
        if os.path.isdir(startpath + "/" + filename):
            listallfiles(startpath + "/" + filename)
        elif filename.lower().endswith(('.flac', '.mp3')):
            files.append(startpath + "/" + filename)

@bot.message_handler(commands=['start'])
def send_files(message):
    startpath = '/run/media/dibusure/aafb7d0a-ca65-4095-b889-daa30025b67f/au'
    listallfiles(startpath)
    for x in files:
        try:
            bot.send_audio(chat_id=chat_id, audio=open(x, 'rb'))
        except telebot.apihelper.ApiTelegramException as e:
            print(str(e))
            sleeptime = int(str(e).split()[-1])
            print("Sleeping", sleeptime)
            time.sleep(sleeptime)
            bot.send_audio(chat_id=chat_id, audio=open(x, 'rb'))


bot.polling(none_stop=True, interval=0)
