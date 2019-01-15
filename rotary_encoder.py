#!/usr/bin/python3
# by William Hofferbert
# watches raspberry pi GPIO pins and translates that
# behavior into midi data. Midi data is accessible to
# other clients through a virtual midi device that is
# created with aminithru, via os.system
import RPi.GPIO as GPIO
import time
import mido
import os
import re

# wait some seconds, so we don't step on MODEP's toes
time.sleep(10)

# set up backend
mido.set_backend('mido.backends.rtmidi')

# midi device naming and setup
name = "GuitarRotaryEncoder"

# system command to set up the midi thru port
# TODO would be nice to do this in python, but
# rtmidi has issues seeing ports it has created
runCmd = "amidithru '" + name + "' &"
os.system(runCmd)

# regex to match on rtmidi port name convention
#GuitarRotaryEncoder:GuitarRotaryEncoder 132:0
# TODO is it necessary to write:  "\s+(\d+)?:\d+)"  instead?
nameRegex = "(" + name + ":" + name + "\s+\d+:\d+)"
matcher = re.compile(nameRegex)
newList = list(filter(matcher.match, mido.get_output_names()))
# all to get the name of the thing we just made
output_name = newList[0]

# use P1 header pin numbering convention, ignore warnings
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

# button midi info; cc#12 = effect control 1 
button_state = 0
button_channel = 0
button_cc_num = 12

# knob midi info; cc#7 = volume, default position near half
position = 63
rotary_increment = 1
rotary_channel = 0
rotary_cc_num = 7

# Set up the GPIO channels
GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # dt
GPIO.setup(19, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # sw
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # clk


def ret_mili_time():
  current_milli_time = int(round(time.time() * 1000))
  return current_milli_time


def short_circuit_time(val):
  global last_time
  myTime = ret_mili_time()
  time_diff = myTime - last_time
  if (time_diff > val):
    last_time = myTime
    return 0
  else:
    return 1


def rotary_callback():
  # rotating clockwise will cause pins to be different
  global position
  global rotary_increment
  if (GPIO.input(19) == GPIO.input(23)):
    # ccw, reduce
    position-=rotary_increment
    if (position < 0):
      position = 0
    #print("ccw, pos = %s", position)
  else:
    # cw
    position+=rotary_increment
    if (position > 127):
      position = 127
    #print("clockwise, pos = %s", position)
  msg = mido.Message('control_change', channel=rotary_channel, control=rotary_cc_num, value=position)
  output = mido.open_output(output_name)
  output.send(msg)


def button_push():
  global button_state
  if (short_circuit_time(220)):
    return
  #print("Button was released!")
  # reset position?
  if (button_state == 1):
    button_state = 0
  else:
    button_state = 1
  midi_state = 127 * button_state
  msg = mido.Message('control_change', channel=button_channel, control=button_cc_num, value=midi_state)
  output = mido.open_output(output_name)
  output.send(msg)


# starting time
last_time = ret_mili_time()

# button
GPIO.add_event_detect(21,GPIO.FALLING,callback=button_push)

# rotary encoder
GPIO.add_event_detect(23,GPIO.BOTH,callback=rotary_callback)

# keep running
while True:
    time.sleep(0.1)
