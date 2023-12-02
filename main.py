#### TODO
#### СОРТИРОВАТЬ ФАЙЛЫ ПО РАЗМЕРУ [X]
#### СПИСОК ОТПРАВЛЕННЫХ ФАЙЛОВ [X] 


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
maxfilesize = 50*2**20

files = []
filesnot = [] # files, that can't be sent 
if os.path.exists('filessent.txt'):
    with open('filessent.txt', 'r') as f:
        filessent = eval(f.read()) # WARNING: remote execution
else:
    filessent = set()

def listallfiles(startpath):
    for filename in os.listdir(startpath):
        fullname = startpath + "/" + filename
        if os.path.isdir(fullname):
            listallfiles(fullname)
        elif filename.lower().endswith(('.flac', '.mp3')):
            if os.path.getsize(fullname) <= maxfilesize and fullname not in filessent:
                files.append(fullname)
            else:
                filesnot.append(fullname)

with open('filesnot.txt', 'w') as f:
    f.write(str(filesnot))

@bot.message_handler(commands=['start'])
def send_files(message):
    startpath = '/run/media/dibusure/aafb7d0a-ca65-4095-b889-daa30025b67f/au'
    listallfiles(startpath)
    for x in files:
        try:
            bot.send_audio(chat_id=chat_id, audio=open(x, 'rb'))
        except telebot.apihelper.ApiTelegramException as e:
            if int(str(e).split()[10].strip(".")) == 429:
                print(str(e))
                sleeptime = int(str(e).split()[-1])
                print("Sleeping", sleeptime)
                time.sleep(sleeptime)
                bot.send_audio(chat_id=chat_id, audio=open(x, 'rb'))
            else:
                print(e)
                with open('filessent.txt', 'w') as f:
                    f.write(str(filessent))
        finally:
            filessent.add(x)


bot.polling(none_stop=True, interval=0)
