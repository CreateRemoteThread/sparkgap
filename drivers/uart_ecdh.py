#!/usr/bin/env python3

from drivers import base
import random
import time
import serial

class DriverInterface(base.BaseDriverInterface):
  def __init__(self):
    super().__init__()
    self.config = {}
    print("Using Simple UART driver")
    # reserved names: samplecount,tracecount,trigger
    pass

  def init(self,frontend=None):
    print("initializing uart")
    self.ser = serial.Serial("/dev/ttyUSB0",9600)
    # self.ser.read(1024)
    self.frontend = frontend
    pass

  def drive(self,in_text=None):
    # next_rand = [random.randint(0,255) for _ in range(0,16)]
    # next_randstr = "e" + "".join(["%02x" % nr for nr in next_rand]) + "\n"
    self.frontend.arm()
    time.sleep(1.0)
    # z for 0x00
    # a for 0xaa
    # f for 0xff
    # r for random privkey.
    self.ser.write(b"z-\n")
    print("Command sent")
    f = self.ser.read(6)
    print("Done")
    return ([0],[0])

  def close(self):
    self.ser.close()
    pass
