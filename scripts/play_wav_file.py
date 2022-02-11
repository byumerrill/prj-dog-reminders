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
import random
import argparse
import subprocess

INT_PAUSE_SECONDS=10
reminder_script_nm=os.path.basename(__file__) 

print (reminder_script_nm + ": Number of Arguments received: " + str(len(sys.argv)))
parser = argparse.ArgumentParser()
parser.add_argument("-wf", "--WavFile", type=str, help="Path to wave file to be played")
parser.add_argument("-i", "--Iterations", type=int, help="Number of times to play the wave file")
args = parser.parse_args()


# Fail if no Arguments
if len(sys.argv) <= 1:
	print(reminder_script_nm + ": !!!!!!!!!!!!!!!!!!!!!!!!!")
	print(reminder_script_nm + ": Error: No Args. Exiting Script.")
	print(reminder_script_nm + ": You must provide the -f argument (aka --File) in order to run this script.")
	print(reminder_script_nm + ": For Example: '-f /my/path/to/file.wav'")
	print(reminder_script_nm + ": !!!!!!!!!!!!!!!!!!!!!!!!!")
	exit(1)


def main():

	global INT_PAUSE_SECONDS

	# Set arg value to variable and force to lower case
	wav_file=args.WavFile
	print(reminder_script_nm + ": wav_file: " + wav_file)

	# Set arg value to variable and force to lower case
	iterations=args.Iterations
	print(reminder_script_nm + ": iterations: " + str(iterations))

	for x in range(iterations):
		print(reminder_script_nm + ": x:" + str(x))
		play_wav(wav_file)
		time.sleep(INT_PAUSE_SECONDS)

if __name__ == '__main__':
	main()


