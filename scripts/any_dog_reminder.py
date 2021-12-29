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

ALERT_WAVS_PATH='/home/pi/Merrill/recordings/dog_potty/alert'
THANK_YOU_WAVS_PATH='/home/pi/Merrill/recordings/dog_potty/thank_you'
ALERT_WAV=random.choice(os.listdir(ALERT_WAVS_PATH))
THANK_YOU_WAV=random.choice(os.listdir(THANK_YOU_WAVS_PATH))

ALERT_FULL_PATH=ALERT_WAVS_PATH + '/' + ALERT_WAV
THANK_YOU_FULL_PATH=THANK_YOU_WAVS_PATH + '/' + THANK_YOU_WAV

SAD_FULL_PATH='/home/pi/Merrill/recordings/dog_potty/western_potty_sad.wav'


MAX_ALERT_LOOPS=8
INT_BLINKS=8
BUTTON_STATE='ON'

DB_NAME='doggyremindersdb'
TBL_EVENTS='reminder_events'
TBL_ASSIGNEE='assignee'
DB_URL='/home/pi/Merrill/sql/' + DB_NAME



def main():

	global DB_URL


	#Connect to sqlite db
	conn=create_sqlite_conn(DB_URL)
	

	reminder_script_nm=os.path.basename(__file__)
	reminder_script_url=Path(__file__).parent.resolve()
	reminder_gmts=time.strftime("%a, %d %b %Y %I:%M:%S %p %Z", time.gmtime())
	reminder_ts=strftime("%a, %d %b %Y %I:%M:%S %p %Z")
	reminder_day_of_wk=strftime("%A")
	reminder_date=strftime("%Y-%m-%d")
	reminder_type='test'


	#query="select * from assignee;"
	query="select max(reminder_id) from " + TBL_EVENTS + " where reminder_id is not null;"

	result_set, rows=run_query(conn, query)


	if rows < 1 :
		print("No rows returned from query")
		query="select assignee_id, first_name from " + TBL_ASSIGNEE + " order by assignee_id asc limit 1;"
		result_set, rows =run_query(conn, query)


	for row in result_set:
		print("ID: ", row[0])
		print("Name: ", row[1])

	conn.close()


####################################################################
	# Debug step to exit early
	sys.exit()
####################################################################


	alert_loop_counter = 1
	global BUTTON_STATE
	global MAX_ALERT_LOOPS
	global SAD_FULL_PATH
	print('LED is ON when button status is ON. Press button again to turn off. (Ctrl-C for exit).')
	with Board() as board:
		with Leds() as leds:
			while True:
				print("alert_loop_counter " + str(alert_loop_counter))

				#If nobody comes after "alert_loop_counter" reaches max, then stop and blink yellow
				if alert_loop_counter > MAX_ALERT_LOOPS:
					leds.pattern = Pattern.breathe(3000)
					leds.update(Leds.rgb_pattern(Color.YELLOW))
					play_wav(SAD_FULL_PATH)
					#"Breathe" YELLOW for 5 minutes to show the alert was NOT resolved
					time.sleep(300)
					sys.exit(0)

				board.button.when_pressed = update_button_state
				if BUTTON_STATE == 'ON':
					#board.led.state = Led.ON

					# After every cycle of INT_BLINKS blinks, play the alert sound
					play_wav(ALERT_FULL_PATH)

					for x in range(INT_BLINKS):
						print(x)

						#Check if the button state changed
						if BUTTON_STATE == 'OFF':
							#break	# break here. Exit the for loop, stop blinking, and stop playing the alert sound
							alert_resolved()
							#board.led.state = Led.OFF
							#play_wav(THANK_YOU_FULL_PATH)
							#sys.exit(0)

						leds.update(Leds.rgb_on(Color.RED))
						time.sleep(1)

						#Check if the button state changed
						if BUTTON_STATE == 'OFF':
							#break	# break here. Exit the for loop, stop blinking, and stop playing the alert sound
							alert_resolved()
							#board.led.state = Led.OFF
							#play_wav(THANK_YOU_FULL_PATH)
							#sys.exit(0)

						leds.update(Leds.rgb_off())
						time.sleep(1)
				else:
					board.led.state = Led.OFF

				#Increment alert loop counter
				alert_loop_counter +=1



def insert_event(sql_conn,tpl_event):
	global TBL_EVENTS

	print("Inserting this tuple into the db: ", tpl_event)
	cur = sql_conn.cursor()
	sql = ''' INSERT INTO ''' + TBL_EVENTS + '''(reminder_script_nm, reminder_script_url, reminder_gmts, reminder_ts, reminder_day_of_wk, reminder_date, reminder_type, assignee_nm, reminder_audio_file_nm, reminder_audio_file_url) values (?,?,?,?,?,?,?,?,?,?) '''
	cur.execute(sql, tpl_event)
	sql_conn.commit()
	return cur.lastrowid





def run_query(sql_conn, str_query):

	print("Running Query: ", str_query)
	cursor=sql_conn.cursor()
	cursor.execute(str_query)
	records=cursor.fetchall()
	if records:
		print("records list is not empty")
	else:
		print("records list is EMPTY!")


	first_row=records[0]
	first_col=first_row[0]
	record_count = len(records)

	# Check for null first_row
	if first_row is None:
		print("first_row is None")
		records=[]
		record_count=0

	# Check for empty String first_row
	elif not first_row:
		print("not first_row  which means EMPTY STRING")
		records=[]
		record_count=0
	else:
		print("Found data in first_row: ", first_row)


	# Check for null first_col
	if first_col is None:
		print("first_col is None")
		records=[]
		record_count=0

	# Check for empty String first_col
	elif not first_col:
		print("not first_col  which means EMPTY STRING")
		records=[]
		record_count=0
	else:
		print("Found data in first_col: ", first_col)

	print("length of records list: ", record_count)
	cursor.close()
	return records, record_count






def create_sqlite_conn(db_file):
	""" create a database connection to a SQLite database """
	conn = None
	try:
		conn = sqlite3.connect(db_file)
		print(sqlite3.version)
	except Error as e:
		print(e)

	return conn



def update_button_state():
	global BUTTON_STATE
	if BUTTON_STATE == 'OFF':
		#print('Button state was OFF. Switching to ON')
		BUTTON_STATE='ON'
	elif BUTTON_STATE == 'ON':
		#print('Button state was ON. Switching to OFF')
		BUTTON_STATE='OFF'
	else:
		print('Button was in an unknown state! Turning off now to be safe...')
		BUTTON_STATE='OFF'
	print(BUTTON_STATE)

def button_print():
	#print('Button has been pressed!')
	update_button_state()

def alert_resolved():
	global THANK_YOU_FULL_PATH
	with Board() as board:
		with Leds() as leds:
			board.led.state = Led.OFF
			play_wav(THANK_YOU_FULL_PATH)
			leds.pattern = Pattern.breathe(3000)
			leds.update(Leds.rgb_pattern(Color.BLUE))
			#"Breathe" blue for 9 seconds to show the alert was resolved
			time.sleep(9)
			sys.exit(0)



if __name__ == '__main__':
	main()

