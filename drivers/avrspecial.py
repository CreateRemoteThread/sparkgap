#!/usr/bin/env python3

if __name__ != "__main__":
  from drivers import base

import random
import time
import serial

# avrspecial format:
# byte '#' : begin command
# byte len : length of transaction
# for i in range(0,len):
#   byte trigger (0xff or 0x0)
#   byte spi-data
# byte '#' : sanity check

class DriverInterface(base.BaseDriverInterface):
  def __init__(self):
    super().__init__()
    self.config = {}
    print("Using AVR Multi Target Board")
    # reserved names: samplecount,tracecount,trigger
    pass

  def fetchUntil(self,waitChar):
    c = None
    out = []
    while c != waitChar:
      c = self.ser.read(1).decode("utf-8")
      out.append(c)
    return out

  def init(self,frontend=None):
    print("Initializing UART to AVR Multi Target")
    self.ser = serial.Serial("/dev/ttyUSB0",9600,timeout=2.0)
    self.frontend = frontend

  def drive(self,in_text=None):
    self.frontend.arm()
    time.sleep(0.5)
    self.ser.write(b"#\x08\xFF\xAC\x00\x53\x00\x00\x00\x00\x00\x20\x00\x00\x00\x00\x00\xFF#")
    x = self.ser.read(1)
    if x != b'#':
      print("Critical Error: expected '#', got ",)
      print(x)
    x = self.ser.read(8)
    print(["%02x" % ix for ix in x])
    return ([0x00] * 16,list(x) + [0xaa] * 8)

  def close(self):
    try:
      self.ser.close()
    except:
      pass


