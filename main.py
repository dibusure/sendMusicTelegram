import telebot
from telebot import types
import os
import json
import time
import signal
import sys
import logging
import shutil

# logging config
logging.basicConfig(level=logging.INFO, filename="bot.log",filemode="w")

# getting token
file = open('token.json')
data = json.load(file)
bot = telebot.TeleBot(data['token'])

# global vars
startpath = '/run/media/dibusure/aafb7d0a-ca65-4095-b889-daa30025b67f/au'
chat_id = '-1002038295546'
maxfilesize = 50*2**20
filesnotpath = startpath + "/" + "filesnot"

# global arrs
files = []
filesnot = [] # files, that can't be sent 

if os.path.exists('filessent.txt'):
    logging.info("filessent.txt exists")

    with open('filessent.txt', 'r') as f:
        filessent = eval(f.read())  # WARNING: remote execution
else:
    print("File not found")
    filessent = set() # blank filessent
    logging.warning("Blank filessent")

# SIGNAL HANDLER
def signal_handler(sig, frame):
    with open('filessent.txt', 'w') as f:
        f.write(str(filessent))
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def listallfiles(startpath):
    for filename in os.listdir(startpath):
        fullname = startpath + "/" + filename # just a nice costyl (dog-nail)
        fullname = fullname.strip() # delete shit from fullname
        if os.path.isdir(fullname):
            listallfiles(fullname) # just a recursive func
        elif filename.lower().endswith(('.flac', '.mp3')):
            if os.path.getsize(fullname) <= maxfilesize and fullname not in filessent: # check if size is nice
                files.append(fullname)
            elif os.path.getsize(fullname) >= maxfilesize: # important compare
                filesnot.append(fullname)
                with open('filesnot.txt', 'w') as f:
                    f.write(str(filesnot))

def copyfilesnot(filesnot, filesnotpath):
    if os.path.isdir(filesnotpath) == False: 
        os.mkdir(filesnotpath)

    for x in filesnot:
        shutil.copy(x, filesnotpath)
        print("Copied", x)
    print("done")

copyfilesnot(filesnot, filesnotpath)

@bot.message_handler(commands=['start'])
def send_files(message):
    listallfiles(startpath)
    for x in files:
        try:
            # send files
            bot.send_audio(chat_id=chat_id, audio=open(x, 'rb'))
            logging.debug("Sent " + x)
        except telebot.apihelper.ApiTelegramException as e:
            if int(str(e).split()[10].strip(".")) == 429:
                print(str(e))
                sleeptime = int(str(e).split()[-1])
                logging.warning("Sleeping", sleeptime)
                time.sleep(sleeptime)
                bot.send_audio(chat_id=chat_id, audio=open(x, 'rb'))
            else:
                print(e)
                with open('filessent.txt', 'w') as f:
                    f.write(str(filessent))
                return 
            
        except Exception as e:
            print(e)
            with open('filessent.txt', 'w') as f:
                f.write(str(filessent))
                logging.warning("Filessent has written")
        finally:
            filessent.add(x)


bot.polling(none_stop=True, interval=0)
