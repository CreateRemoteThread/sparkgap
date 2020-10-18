#!/usr/bin/env python3

import sys
import serial

ser = serial.Serial("/dev/ttyUSB0",timeout=2.0)
while True:
  ser.write(b"#\x08\xFF\xAC\x00\x53\x00\x00\x00\x00\x00\x20\x00\x00\x00\x00\x00\xFF#")
  x = ser.read(1)
  if x != b'#':
    print("Error")
    print(x)
    sys.exit(0)
  print(ser.read(8))
  sys.exit(0)
