#!/usr/bin/env python3

# one-off target board read (confirming functionality

import sys
import serial

ser = serial.Serial("/dev/ttyUSB0",timeout=2.0)
while True:
  ser.write(b"#\x08\x00\xAC\x00\x53\x00\x00\x00\x00\xFF\x28\xFF\x00\xFF\x00\x00\xFF#")
  x = ser.read(1)
  if x != b'#':
    print("Error")
    print(x)
    sys.exit(0)
  print(["%02x" % x for x in ser.read(8)])
  sys.exit(0)
