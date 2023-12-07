import telebot
from telebot import types
import os
import json
import time
import signal
import sys
import shutil
import yt_dlp

# getting token
file = open('token.json')
data = json.load(file)
bot = telebot.TeleBot(data['token'])

# global vars
startpath = '/run/media/dibusure/aafb7d0a-ca65-4095-b889-daa30025b67f/mu'
chat_id = '-1002038295546'
maxfilesize = 50*2**20
filesnotpath = startpath + "/" + "filesnot"

# global arrs
files = []
filesnot = [] # files, that can't be sent 
filesnotcopied = [] # for interrupt
downloaded =[]

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

    with open("downloaded.txt", 'w') as f:
        f.write(str(downloaded))
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

@bot.message_handler(commands=['send'])
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

@bot.message_handler(commands=['down'])
def downloadfiles(message):
    if len(sys.argv) == 0:
        print("Please use:\npython main.py [FILE]\inWhere [FILE] is a path to file with youtube/YTM links for playlists/albums")
        sys.exit(-1)
    else:
        if os.path.exists(sys.argv[1]):
            with open(sys.argv[1], 'r') as f:
                links = (f.read()).split("\n")  # WARNING: remote execution
                links = [i.strip(' ') for i in links]
                links = [i.strip('') for i in links]
        else:
            print("File not found")
            sys.exit(-1)

    ytdl_opts = {
        'outtmpl': startpath + "/" + '%(artist)s/%(release_year)s - %(album)s/%(title)s',
        'format': 'bestaudio/best',
        'extractaudio':True,
        'audioformat':'flac',
        'addmetadata':True,
        'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            },
            {
                'key': 'FFmpegMetadata'
            }]
    }

    while downloaded != links:
        with yt_dlp.YoutubeDL(ytdl_opts) as ytdl:
            for i in links:
                ytdl.download([i])
                print("Downloaded", i)
                downloaded.append(i)
            print("Done")

bot.polling(none_stop=True, interval=0)
