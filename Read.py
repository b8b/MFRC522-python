#!/usr/bin/env python
# -*- coding: utf8 -*-
#
#    Copyright 2014,2018 Mario Gomez <mario.gomez@teubi.co>
#
#    This file is part of MFRC522-Python
#    MFRC522-Python is a simple Python implementation for
#    the MFRC522 NFC Card Reader for the Raspberry Pi.
#
#    MFRC522-Python is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    MFRC522-Python is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with MFRC522-Python.  If not, see <http://www.gnu.org/licenses/>.
#

import RPi.GPIO as GPIO
import MFRC522
import signal
import os
import time
import subprocess
import sys

continue_reading = True

# Capture SIGINT for cleanup when the script is aborted
def end_read(signal,frame):
    global continue_reading
    print "Ctrl+C captured, ending read."
    continue_reading = False
    GPIO.cleanup()

# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()

# Welcome message
print "Welcome to the MFRC522 data read example"
print "Press Ctrl-C to stop."

current_uid = None

# This loop keeps checking for chips. If one is near it will get the UID and authenticate
while continue_reading:
    
    # Scan for cards    
    (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

    # If a card is found
    if status != MIFAREReader.MI_OK:
        time.sleep(0.2)
        continue
    
    # Get the UID of the card
    (status,uid) = MIFAREReader.MFRC522_Anticoll()

    # If we have the UID, continue
    if status == MIFAREReader.MI_OK:
        if uid == current_uid:
          continue

        tags = {}
        with open("/home/pi/work/MFRC522-python/tags.dat", "r") as fil:
          for line in fil:
            k, v = line.rstrip('\n').split(' ', 1)
            tags[k] = v
        k = "%d,%d,%d,%d" % (uid[0], uid[1], uid[2], uid[3])
        if k in tags:
          v = tags[k]
          if (v.startswith("x ")):
            if (v.startswith("x volume ")):
              subprocess.call(["mpc", "volume", v[9:]])
            else:
              sys.stderr.write("invalid command: %s\n" % (v))
          else:
            subprocess.call(["mpc", "clear"])
            if (v.startswith("l ")):
              subprocess.call(["mpc", "load", v[2:]])
            elif (v.startswith("p ")):
              subprocess.call(["mpc", "add", v])
            else:
              subprocess.call(["mpc", "add", v])
            subprocess.call(["mpc", "play"])
            current_uid = uid
        else:
          sys.stderr.write("card not in database: %s\n" % (k))
          current_uid = uid

