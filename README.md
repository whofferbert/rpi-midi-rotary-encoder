# rpi-midi-rotary-encoder

rotary_encoder.py

A python script to create a midi device, and send control change messages out through it.

```python
import RPi.GPIO as GPIO
import time
import mido
import os
import re
```

Also requires 'amidithru'

For a first time setup on a pi, you may have to install rpi.gpio for python3:

```bash
sudo apt-get update
sudo apt-get install python3-rpi.gpio 
```

The script is hopefully laid out clearly enough that customizing and adjusting things should be easy.

Common usage would be to put it on a Raspberry Pi which is connected to a rotary encoder, and run this script to monitor the voltage changes and relay appropriate midi data out through a chosen virtual interface, usable to other software running on the Pi.

Generally, add an entry to your crontab to call the script on startup:
(Make sure you set your path properly)

```bash
@reboot /usr/bin/sudo /path/to/rotary_encoder.py &
```
