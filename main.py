import telebot
from telebot import types
import os
import json
import time
import signal
import sys
import shutil

# getting token
file = open('token.json')
data = json.load(file)
bot = telebot.TeleBot(data['token'])

# global vars
if sys.argv[1] == "metal":
    startpath = '/run/media/dibusure/Files/Music' + '/metal'
    chat_id = '-1001681284273'
elif sys.argv[1] == "soft":
    startpath = '/run/media/dibusure/Files/Music/soft'
    chat_id = '-1001681341097'
else:
   print('please specify the channel name') 
   sys.exit(0)

maxfilesize = 50*2**20
filesnotpath = startpath + "/" + "filesnot"

# global arrs
files = []
filesnot = [] # files, that can't be sent 
filesnotcopied = [] # for interrupt

if os.path.exists('filessent.txt'):
    with open('filessent.txt', 'r') as f:
        filessent = eval(f.read())  # WARNING: remote execution
else:
    print("File not found")
    filessent = set() # blank filessent


# SIGNAL HANDLER
def signal_handler(sig, frame):
    with open('filessent.txt', 'w') as f:
        f.write(str(filessent))

    with open('filesnot.txt', 'w') as f:
        f.write(str(filesnotcopied))
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def listallfiles(startpath):
    for filename in os.listdir(startpath):
        fullname = startpath + "/" + filename # just a nice costyl (dog-nail)
        fullname = fullname.strip() # delete shit from fullname
        if os.path.isdir(fullname):
            listallfiles(fullname) # just a recursive func
        elif filename.lower().endswith(('.flac', '.mp3', '.alac')):
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
        filesnotcopied.append(x)
    print("Done")

@bot.message_handler(commands=['s'])
def send_files(message):
    copyfilesnot(filesnot, filesnotpath)

    listallfiles(startpath)
    for x in files:
        try:
            # send files
            bot.send_audio(chat_id=chat_id, audio=open(x, 'rb'))
        except telebot.apihelper.ApiTelegramException as e:
            if int(str(e).split()[10].strip(".")) == 429:
                print(str(e))
                sleeptime = int(str(e).split()[-1])
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
        finally:
            filessent.add(x)

bot.polling(none_stop=True, interval=0)
