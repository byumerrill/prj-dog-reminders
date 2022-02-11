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



def main():

	for x in range(2):
		print("x:" + str(x))
		print("ASLAN IS SPEAKING!")
		play_wav("/home/pi/Merrill/recordings/dog_potty/thank_you/Minnie_aslan_thanks.wav")
		print("ASLAN HAS SPOKEN!")
		time.sleep(5)

if __name__ == '__main__':
	main()


