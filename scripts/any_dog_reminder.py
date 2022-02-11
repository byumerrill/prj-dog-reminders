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
import os, signal
import pathlib
from pathlib import Path
import sys
import random
import argparse
import subprocess

# Number of family members who could be assigned to take action on a reminder
INT_TOTAL_AVAILABLE_ASSIGNEES=4

# Maximum number of times an alert sound could be played (when waiting for alert resolution)
INT_MAX_ALERT_LOOPS=5

# Number of seconds to pause between each loop (when waiting for alert resolution)
INT_LOOP_PAUSE_SECONDS=10

# Number of seconds to for button blink "sad" yellow if alert is not resolved before timeout
INT_SAD_BLINK_SECONDS=60

BUTTON_STATE='ON'
DB_NAME='doggyremindersdb'
TBL_EVENTS='reminder_events'
TBL_ASSIGNEE='assignee'
DB_URL='/home/pi/Merrill/databases/' + DB_NAME
CURR_ASSIGNEE_NM=''
CURR_ASSIGNEE_ID=''
REMINDER_RESOLVED_TS=''


print ("Number of Arguments received: " + str(len(sys.argv)))
parser = argparse.ArgumentParser()
parser.add_argument("-rt", "--ReminderType", type=str, help="Reminder Type, ex: 'potty' or 'feed'")
args = parser.parse_args()



# Fail if no Arguments
if len(sys.argv) <= 1:
	print("!!!!!!!!!!!!!!!!!!!!!!!!!")
	print("Error: No Args. Exiting Script.")
	print("You must provide the -rt argument (aka --ReminderType) in order to run this script.")
	print("For Example: '-rt potty' or '-rt feed'")
	print("!!!!!!!!!!!!!!!!!!!!!!!!!")
	exit(1)

TimerStartTime= time.time()
#TimerStartTime:1640987265.4756098
print("TimerStartTime:" + str(TimerStartTime))



# Change the sound volume any time by running the command: `alsamixer` (normally set to 60)


## Record new audio files using this script, Ex: 
# cd /home/pi/AIY-voice-kit-python/src/examples/voice
# ./voice_recorder.py -f /home/pi/Merrill/recordings/dog_potty/alert/western_potty_alert.wav
# ./voice_recorder.py -f /home/pi/Merrill/recordings/dog_potty/thank_you/western_potty_thank_you.wav 
# 

BASE_PATH="/home/pi/Merrill/"
SCRIPTS_PATH=BASE_PATH + "prj-dog-reminders/scripts/"
AUDIO_REC_PATH=BASE_PATH + "/recordings/"
REMINDER_AUDIO_PARENT_DIR=""
WAV_PLAYER_SCRIPT_NM="play_wav_file.py"
WAV_KILLER_SCRIPT_NM="kill_wav.sh"
WAV_KILLER_SCRIPT_PATH=SCRIPTS_PATH + WAV_KILLER_SCRIPT_NM


# Set arg value to variable and force to lower case
REMINDER_TYPE=args.ReminderType
REMINDER_TYPE=REMINDER_TYPE.lower()
print("REMINDER_TYPE: " + REMINDER_TYPE)


# Next, evaluate REMINDER_TYPE 
# Determine correct reconrdings to use based on reminder type
if REMINDER_TYPE == "feed":
	REMINDER_AUDIO_PARENT_DIR="/dog_feeding/"
elif  REMINDER_TYPE == "potty":
	REMINDER_AUDIO_PARENT_DIR="/dog_potty/"
else:
	print("!!!!!!!!!!!!!!!!!!!!!!!!!")
	print("Error: invalid value for -rt argument (REMINDER_TYPE variable).")
	print("You must provide the -rt argument (aka --ReminderType) in order to run this script.")
	print("For Example: '-rt potty' or '-rt feed'")
	print("!!!!!!!!!!!!!!!!!!!!!!!!!")
	exit(1)	

ALERT_WAVS_PATH=AUDIO_REC_PATH + REMINDER_AUDIO_PARENT_DIR + '/alert/'
THANK_YOU_WAVS_PATH=AUDIO_REC_PATH + REMINDER_AUDIO_PARENT_DIR + '/thank_you/'
SAD_WAVS_PATH=AUDIO_REC_PATH + REMINDER_AUDIO_PARENT_DIR + '/sad/'

ALERT_FULL_PATH=''
THANK_YOU_FULL_PATH=''
SAD_FULL_PATH=''



def main():

	global ALERT_WAVS_PATH
	global THANK_YOU_WAVS_PATH
	global SAD_WAVS_PATH
	global DB_URL
	global REMINDER_TYPE
	global ALERT_FULL_PATH
	global THANK_YOU_FULL_PATH
	global SAD_FULL_PATH


	# Validate paths
	pathsToValidate = [
		BASE_PATH, 
		SCRIPTS_PATH, 
		AUDIO_REC_PATH, 
		WAV_KILLER_SCRIPT_PATH, 
		ALERT_WAVS_PATH, 
		THANK_YOU_WAVS_PATH, 
		SAD_WAVS_PATH
	]
	testPathsOrFiles(pathsToValidate)

	# Randomly choose a recording to play for the initial alert, thank you response (when alert is resolved), and sad response (when alert times out)
	ALERT_WAV=random.choice(os.listdir(ALERT_WAVS_PATH))
	THANK_YOU_WAV=random.choice(os.listdir(THANK_YOU_WAVS_PATH))
	SAD_WAV=random.choice(os.listdir(SAD_WAVS_PATH))


	ALERT_FULL_PATH=ALERT_WAVS_PATH + '/' + ALERT_WAV
	THANK_YOU_FULL_PATH=THANK_YOU_WAVS_PATH + '/' + THANK_YOU_WAV
	SAD_FULL_PATH=SAD_WAVS_PATH + '/' + SAD_WAV

	# Validate files
	pathsToValidate = [
		ALERT_FULL_PATH,
		THANK_YOU_WAVS_PATH,
		SAD_FULL_PATH,
	]
	testPathsOrFiles(pathsToValidate)


	#Connect to sqlite db
	conn=create_sqlite_conn(DB_URL)
	

	reminder_script_nm=os.path.basename(__file__)
	reminder_script_url=str(Path(__file__).parent.resolve())
	reminder_gmts=time.strftime("%a, %d %b %Y %I:%M:%S %p %Z", time.gmtime(TimerStartTime))
	reminder_ts=strftime("%a, %d %b %Y %I:%M:%S %p %Z", time.localtime(TimerStartTime))
	reminder_day_of_wk=strftime("%A", time.localtime(TimerStartTime))
	reminder_date=strftime("%Y-%m-%d", time.localtime(TimerStartTime))
	#reminder_type='test'


	# First, determine who the next assignee should be, by referncing the most recent reminder.
	#query="select * from assignee;"
	#query="select max(reminder_id) from " + TBL_EVENTS + " where reminder_id is not null;"
	#query="select COALESCE(assignee_id,1) from " + TBL_EVENTS + " where reminder_id is not null order by reminder_id DESC limit 1;"
	query="select re.assignee_id, a.first_name from " + TBL_EVENTS + " re inner join " + TBL_ASSIGNEE + " a on re.assignee_id=a.assignee_id where reminder_id is not null order by reminder_id DESC limit 1;"
	result_set, rows=run_query(conn, query)

	# If there is no pre-existing reminders in the db, get the first assignee, by ID
	if rows < 1 :
		print("No rows returned from query")
		query="select assignee_id, first_name from " + TBL_ASSIGNEE + " order by assignee_id asc limit 1;"
		result_set, rows =run_query(conn, query)
	else:
		# get the next helper's ID and name
		for row in result_set:
			PREV_ASSIGNEE_ID=row[0]
			PREV_ASSIGNEE_NM=row[1]
			print("Assignee ID: ", PREV_ASSIGNEE_ID)
			print("Assignee Name: ", PREV_ASSIGNEE_NM)
		
		# Increment assignee ID, to select the next person. If > INT_TOTAL_AVAILABLE_ASSIGNEES then go back to 1
		x=PREV_ASSIGNEE_ID + 1
		if x > INT_TOTAL_AVAILABLE_ASSIGNEES: x=1

		print("x: " + str(x))
		query="select a.assignee_id, a.first_name from " + TBL_ASSIGNEE + " a where a.assignee_id=" + str(x) + " limit 1;"
		result_set, rows=run_query(conn, query)


	for row in result_set:
		CURR_ASSIGNEE_ID=row[0]
		CURR_ASSIGNEE_NM=row[1]
		print("Assignee ID: ", CURR_ASSIGNEE_ID)
		print("Assignee Name: ", CURR_ASSIGNEE_NM)



	# Next insert the new reminder event into the db using "insert_event" function
	# sql = ''' INSERT INTO ''' + TBL_EVENTS + '''(reminder_script_nm, reminder_script_url, reminder_gmts, reminder_ts, reminder_day_of_wk, reminder_date, reminder_type, assignee_nm, reminder_audio_file_nm, reminder_audio_file_url) values (?,?,?,?,?,?,?,?,?,?) '''	
	#reminder_event = (reminder_script_nm, reminder_script_url, reminder_gmts, reminder_ts, reminder_day_of_wk, reminder_date, reminder_type,CURR_ASSIGNEE_NM, 'DUMMY AUDIO FILE NAME', 'DUMMY AUDIO FILE URL' )
	reminder_event = (reminder_script_nm, reminder_script_url, reminder_gmts, reminder_ts, reminder_day_of_wk, reminder_date, REMINDER_TYPE,CURR_ASSIGNEE_ID, ALERT_WAV, ALERT_FULL_PATH)
	insert_result=insert_event(conn, reminder_event)
	print("Result of attempted insert: ", insert_result)
	
	# Close DB Connection
	conn.close()


	
	#randomInt=random.randrange(1,10)
	#print("random: " + str(randomInt))
	#time.sleep(randomInt)

	# Stop Timer
	TimerEndtTime= time.time()
	print("TimerEndtTime:" + str(TimerEndtTime))

	# Calculate assignee response time
	TimerElapsedTime = TimerEndtTime - TimerStartTime
	print("TimerElapsedTime: " + str(TimerElapsedTime))	

####################################################################
	# Debug step to exit early
	#sys.exit()
####################################################################


	alert_loop_counter = 1
	global BUTTON_STATE
	global INT_MAX_ALERT_LOOPS
	global WAV_PLAYER_SCRIPT_NM

	wav_player_full_path=reminder_script_url + "/" + WAV_PLAYER_SCRIPT_NM
	testPathsOrFiles([wav_player_full_path])


	# Start a sub process that runs in the background, and have it loop through the alert
	p=subprocess.Popen([wav_player_full_path, '-wf', ALERT_FULL_PATH, '-i', str(INT_MAX_ALERT_LOOPS)])
	print("Sub process id: " + str(p.pid))


	print('LED is ON when button status is ON. Press button again to turn off. (Ctrl-C for exit).')
	with Board() as board:
		with Leds() as leds:
			while True:

				print("alert_loop_counter " + str(alert_loop_counter) + "| INT_MAX_ALERT_LOOPS: " + str(INT_MAX_ALERT_LOOPS))

				# Start blinking red, until alert is resolved
				if alert_loop_counter == 1 :
					leds.pattern = Pattern.breathe(2000)
					leds.update(Leds.rgb_pattern(Color.RED))

				# Brief pause
				time.sleep(INT_LOOP_PAUSE_SECONDS)

				#If nobody comes after "alert_loop_counter" reaches max, then stop and blink yellow and exit script
				if alert_loop_counter > INT_MAX_ALERT_LOOPS:

					# Terminate the process that is playing the alert on loop
					print("Terminating " + str(p.pid) + " the process that is playing the alert on loop")
					os.kill(p.pid, signal.SIGTERM)
					print("Waiting for Termination of " + str(p.pid) + " the process that is playing the alert on loop")
					p.wait()
					print("Process Terminated " + str(p.pid) + " the process that is playing the alert on loop")


					# Sometimes the wav alert is still playing even though the alert script was killed.
					# Make sure the 'aplay' program is not still playing any wavs
					kill_sounds()

					# Update button light to "sad" yellow blinking
					leds.pattern = Pattern.breathe(3000)
					leds.update(Leds.rgb_pattern(Color.YELLOW))
					
					#time.sleep(5)
					# Play the sad recording
					print("Now playing the sad recording: " + SAD_FULL_PATH)
					p=subprocess.Popen([wav_player_full_path, '-wf', SAD_FULL_PATH, '-i', '1'])
					print("Sub process id: " + str(p.pid))					
					#"Breathe" YELLOW for INT_SAD_BLINK_SECONDS to show the alert was NOT resolved, then exit script
					time.sleep(INT_SAD_BLINK_SECONDS)
					sys.exit(0)

				board.button.when_pressed = update_button_state

				if BUTTON_STATE == 'OFF':
					print("Someone has come to resolve the alert! Someone has physically pushed the button!")
					# Stop Blinking
					board.led.state = Led.OFF

					# Terminate the process that is playing the alert on loop
					print("Terminating " + str(p.pid) + " the process that is playing the alert on loop")
					os.kill(p.pid, signal.SIGTERM)
					print("Waiting for Termination of " + str(p.pid) + " the process that is playing the alert on loop")
					p.wait()
					print("Process Terminated " + str(p.pid) + " the process that is playing the alert on loop")
					
					# Make sure the 'aplay' program is not still playing any wavs
					kill_sounds()

					# Play the gratitude message
					alert_resolved()


				# Increment alert loop counter
				alert_loop_counter +=1



def kill_sounds():
	print("Executing fuction: 'kill_sounds())'")
	global WAV_KILLER_SCRIPT_PATH
	
	print("Making sure all 'aplay' commands are stopped before playing sad recording.")
	pStopSound=subprocess.Popen([WAV_KILLER_SCRIPT_PATH])
	print("Sub process id of pStopSound: " + str(pStopSound.pid))
	print("Waiting for pStopSound to finish")
	pStopSound.wait()
	print("Process pStopSound finished: " + str(pStopSound.pid))


def insert_event(sql_conn,tpl_event):
	print("Executing fuction: 'insert_event(sql_conn,tpl_event)'")
	global TBL_EVENTS

	print("Inserting this tuple into the db: ", tpl_event)
	cur = sql_conn.cursor()
	sql = ''' INSERT INTO ''' + TBL_EVENTS + '''(reminder_script_nm, reminder_script_url, reminder_gmts, reminder_ts, reminder_day_of_wk, reminder_date, reminder_type, assignee_id, reminder_audio_file_nm, reminder_audio_file_url) values (?,?,?,?,?,?,?,?,?,?) '''
	cur.execute(sql, tpl_event)
	sql_conn.commit()
	return cur.lastrowid



def run_query(sql_conn, str_query):
	print("Executing fuction: 'run_query(sql_conn, str_query)'")
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
	print("Executing fuction: 'create_sqlite_conn(db_file)'")
	""" create a database connection to a SQLite database """
	testPathsOrFiles([db_file])
	conn = None
	print('Connecting to db:"', db_file, '"') 
	try:
		conn = sqlite3.connect(db_file)
		print(sqlite3.version)
	except Error as e:
		print(e)

	return conn



def update_button_state():
	global BUTTON_STATE
	if BUTTON_STATE == 'OFF':
		print('Button state was OFF. Switching to ON')
		BUTTON_STATE='ON'
	elif BUTTON_STATE == 'ON':
		print('Button state was ON. Switching to OFF')
		BUTTON_STATE='OFF'
	else:
		print('Button was in an unknown state! Turning off now to be safe...')
		BUTTON_STATE='OFF'
	#print(BUTTON_STATE)



def alert_resolved():
	print("Executing fuction: 'alert_resolved()'")
	REMINDER_RESOLVED_TS=strftime("%a, %d %b %Y %I:%M:%S %p %Z")
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
			

def testPathsOrFiles(pathList):
	print("Executing fuction: 'testPathsOrFiles(pathList)'")
	print("The length of pathList is: " + str(len(pathList)))
	list_loop_counter =1
	for thisPath in pathList:
		# Validate the given directory or file is valid
		isValidFile = os.path.isfile(thisPath) 
		isValidDir = os.path.isdir(thisPath)
		if isValidDir:
			print("path (" + str(list_loop_counter) + "): " + thisPath + " is a valid directory." )
		elif isValidFile:
			print("path (" + str(list_loop_counter) + "): " + thisPath + " is a valid file." )
		else:
			print("ERROR: path (" + str(list_loop_counter) + "): " + thisPath + " is NEITHER a valid DIRECTORY NOR is it a valid FILE." )
			print("Exiting script.")
			exit(1)
		list_loop_counter +=1

if __name__ == '__main__':
	main()

