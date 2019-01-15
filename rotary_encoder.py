#!/usr/bin/python3
# by William Hofferbert
# watches raspberry pi GPIO pins and translates that
# behavior into midi data. Midi data is accessible to
# other clients through a virtual midi device that is
# created with amidithru, via os.system

import RPi.GPIO as GPIO
import time
import mido
import os
import re

#
# script setup
#

# midi device naming and setup
name = "GuitarRotaryEncoder"

# set up pi GPIO pins for rotary encoder
sw_pin = 19
dt_pin = 21
clk_pin = 23

# button midi info; cc#12 = effect control 1 
button_state = 0
button_channel = 0
button_cc_num = 12
# don't let button signals trigger until X ms have passed
button_stagger_time = 220

# knob midi info; cc#7 = volume, default position near half
position = 63
rotary_increment = 1
rotary_channel = 0
rotary_cc_num = 7

# wait some seconds for other software after reboot
init_sleep_secs = 10

#
# subroutines
#

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


def send_cc(channel, ccnum, val):
  msg = mido.Message('control_change', channel=channel, control=ccnum, value=val)
  output = mido.open_output(output_name)
  output.send(msg)


def rotary_callback(unused):
  # rotating clockwise will cause pins to be different
  global position
  global rotary_increment
  # rotary encoder voltages are equal when going counter-clockwise
  if (GPIO.input(sw_pin) == GPIO.input(clk_pin)):
    position -= rotary_increment
    if (position < 0):
      position = 0
    #print("counterclockwise, pos = %s", position)
  else:
    position += rotary_increment
    if (position > 127):
      position = 127
    #print("clockwise, pos = %s", position)
  send_cc(rotary_channel, rotary_cc_num, position)


def button_push(unused):
  global button_state
  global button_stagger_time
  # do not trigger button actions unless 220 ms have passed
  if (short_circuit_time(button_stagger_time)):
    return
  #print("Button was released!")
  if (button_state == 1):
    button_state = 0
  else:
    button_state = 1
  midi_state = 127 * button_state
  send_cc(button_channel, button_cc_num, midi_state)

#
# main stuff below
# TODO maybe use the pythonic if __name__ == "__main__":
#

# use P1 header pin numbering convention, ignore warnings
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

# Set up the GPIO channels
GPIO.setup(dt_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # dt
GPIO.setup(sw_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # sw
GPIO.setup(clk_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # clk

# wait some seconds, so we don't step on MODEP's toes
time.sleep(init_sleep_secs)

# set up backend
mido.set_backend('mido.backends.rtmidi')

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

# starting time
last_time = ret_mili_time()

# button
GPIO.add_event_detect(dt_pin,GPIO.FALLING,callback=button_push)

# rotary encoder
GPIO.add_event_detect(clk_pin,GPIO.BOTH,callback=rotary_callback)

# keep running
while True:
    time.sleep(0.1)
