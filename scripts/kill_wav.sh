#!/bin/bash

# 
# Put simply, this script will look for an active process running the "aplay" command and kill it. 
# This allows me to immeditely turn off a wav file that is playing, so that I can play a new sound 
# (ensuring that two wav files are not playing at once, wich is possible)
# 

# find a process that is running hte "aplay" command and save into variable


thisScript=`basename "$0"`
targetPid=`pgrep -f aplay`


if [ -z "${targetPid}" ]
then
	echo "${thisScript}: No process found running 'aplay' command"
	exit 1
else
	echo "${thisScript}: Found a process running 'aplay', with pid: ${targetPid}"
	echo "${thisScript}: Now killing process id: ${targetPid}"

	# Kill the process (stopping the sound that is playing)
	kill -9 ${targetPid}
fi
