import sys
import yt_dlp
import os
import shutil
import signal

if len(sys.argv) > 0:
    if os.path.exists(sys.argv[2]):
        with open(sys.argv[2], 'r') as f:
            links = (f.read()).split("\n")  # WARNING: remote execution
            links = [i.strip() for i in links]
    else:
        print("File not found")
        sys.exit(-1)
else:
    print("Please use:\npython main.py [FILE]\inWhere [FILE] is a path to file with youtube/YTM links for playlists/albums")
    sys.exit(-1)

startpath = '/run/media/dibusure/Files/Music' + sys.argv[1]
if sys.argv[1] == 'soft' or sys.argv[1] == 'metal':
    startpath = '/run/media/dibusure/Files/Music' + '/' + sys.argv[1]
else:
    print("Invalid channel")
    sys.exit(1)
filesnotpath = startpath + "/" + "filesnot"
downloaded = []
copied = []
filesnot = []
maxfilesize = 50*2**20

if os.path.exists('downloaded.txt'):
    with open('downloaded.txt', 'r') as f:
        downloaded = eval(f.read())  # WARNING: remote execution

def signal_handler(sig, frame):
    with open('downloaded.txt', 'w') as f:
        f.write(str(downloaded))

    with open('copied.txt', 'w') as f:
        f.write(str(copied))
    sys.exit(0)



signal.signal(signal.SIGINT, signal_handler)
def downloadfiles(links, downloadpath):
    ytdl_opts = {
        'outtmpl': downloadpath + "/" + '%(artist)s/%(release_year)s - %(album)s/%(title)s',
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'addmetadata': True,
        'quiet': True,
        'continue': True,
        'ignore-errors': True,
        'no-abort-on-error': True,
        'write-thumbnail': True,
        'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            },
            {
                'key': 'FFmpegMetadata'
            }]
    }

    with yt_dlp.YoutubeDL(ytdl_opts) as ytdl:
        for i in links:
            if i == ' ' or i == '':
                print('empty link :(')
            elif i != ' ':
                try:
                    ytdl.download([i])
                    print("----------------------------------------------------")
                    print("Downloaded", i)
                    print("----------------------------------------------------")
                    downloaded.append(i)
                except Exception as e:
                    print(e)
                    with open('downloaded.txt', 'w') as f:
                        f.write(str(downloaded))
                finally:
                    print("finally!")

if list(set(links) - set(downloaded)) != ' ':
    downloadfiles(list(set(links) - set(downloaded)), startpath)
else:
    print("Done")
