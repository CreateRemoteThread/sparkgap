#!/usr/bin/env python3

if __name__ != "__main__":
  from drivers import base

import random
import time
import serial

class DriverInterface(base.BaseDriverInterface):
  def __init__(self):
    super().__init__()
    self.config = {}
    print("Using Buspirate SPI Driver")
    # reserved names: samplecount,tracecount,trigger
    pass

  def fetchUntil(self,waitChar):
    c = None
    while c != waitChar:
      c = ser.read(1).decode("utf-8")

  def init(self,frontend=None):
    print("initializing uart")
    self.ser = serial.Serial("/dev/ttyUSB0",115200)
    self.ser.write(b"#\n")
    time.sleep(0.25)
    self.fetchUntil(">")
    self.ser.write(b"m5412122\n")
    time.sleep(0.25)
    self.fetchUntil(">")
    
    self.frontend = frontend

  def drive(self,in_text=None):
    next_rand = [random.randint(0,255) for _ in range(0,16)]
    next_randstr = "e" + "".join(["%02x" % nr for nr in next_rand]) + "\n"
    self.frontend.arm()
    time.sleep(1.0)
    self.ser.write(next_randstr.encode("utf-8"))
    print("Written")
    f = self.ser.read(32 + 3)[1:33]
    print("OK %s" % f)
    # grab newline
    return (next_rand,[0xAA] * 16)


  def close(self):
    self.ser.close()
    pass
