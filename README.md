# rpi-midi-rotary-encoder

rotary_encoder.py

```python
import RPi.GPIO as GPIO
import time
import mido
import os
import re
```

Also requires 'amidithru'

A python script to create a midi device, and send control change messages out through it.

The script was written with variables to make customizing things easy as possible.

Common usage would be to put it on a Raspberry Pi which is connected to a rotary encoder, and run this script to monitor the voltage changes and relay appropriate midi data out through a chosen virtual interface, usable to other software running on the Pi.

Generally, add an entry to your crontab to call the script on startup:
(Make sure you set your path properly)

```bash
@reboot /usr/bin/sudo /path/to/rotary_encoder.py
```
