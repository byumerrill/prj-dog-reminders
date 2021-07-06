#!/usr/bin/env python3

from aiy.board import Board, Led, Pattern
from aiy.voice.audio import AudioFormat, play_wav, record_file
import time, os, random, sys, traceback
from aiy.leds import Leds, Color
from datetime import datetime

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


MAX_ALERT_LOOPS=4
BUTTON_STATE='ON'

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

def main():
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

                    # After every cycle of 4 blinks, play the alert sound    
                    play_wav(ALERT_FULL_PATH)

                    for x in range(4):
                        print(x)

                        #Check if the button state changed
                        if BUTTON_STATE == 'OFF':
                            #break    # break here. Exit the for loop, stop blinking, and stop playing the alert sound
                            alert_resolved()
                            #board.led.state = Led.OFF
                            #play_wav(THANK_YOU_FULL_PATH)
                            #sys.exit(0)                        
                        
                        leds.update(Leds.rgb_on(Color.RED))
                        time.sleep(1)
                        
                        #Check if the button state changed
                        if BUTTON_STATE == 'OFF':
                            #break    # break here. Exit the for loop, stop blinking, and stop playing the alert sound
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



if __name__ == '__main__':
    main()

