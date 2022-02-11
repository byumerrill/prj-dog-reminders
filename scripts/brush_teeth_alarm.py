#!/usr/bin/env python3

from aiy.board import Board, Led, Pattern
from aiy.voice.audio import AudioFormat, play_wav, record_file
import time, os, random, sys, traceback
from aiy.leds import Leds, Color
from datetime import datetime
import sqlite3
from sqlite3 import Error
import time
from time import gmtime, strftime
import os
import pathlib
from pathlib import Path
import sys


startTime = datetime.now()

# Change the sound volume any time by running the command: `alsamixer`


## Record new audio files using this script, Ex: 
# cd /home/pi/AIY-voice-kit-python/src/examples/voice
# ./voice_recorder.py -f /home/pi/Merrill/recordings/dog_potty/alert/western_potty_alert.wav
# ./voice_recorder.py -f /home/pi/Merrill/recordings/dog_potty/thank_you/western_potty_thank_you.wav 
# 

MUSIC_PATH='/home/pi/Music'
MUSIC_FILE='raffi-brush-your-teeth.wav'

ALERT_FULL_PATH=MUSIC_PATH + '/' + MUSIC_FILE

MAX_ALERT_LOOPS=2



def main():

	global ALERT_FULL_PATH
	global MAX_ALERT_LOOPS
	
	alert_loop_counter = 1


	print('ALERT_FULL_PATH: ' + ALERT_FULL_PATH)
	

####################################################################
	# Debug step to exit early
#	sys.exit()
####################################################################


	play_wav(ALERT_FULL_PATH)
	play_wav(ALERT_FULL_PATH)



if __name__ == '__main__':
	main()

