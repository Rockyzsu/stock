#-*-coding=utf-8-*-
# play sound in python
import os, subprocess
def play():
    media_path = "ios.wav"
    p = subprocess.Popen(['mplayer', media_path], stdout=subprocess.PIPE)
    p.communicate()
    p.wait()