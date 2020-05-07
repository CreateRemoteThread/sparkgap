#!/usr/bin/env python3

# standard usart driver.
import random
import time
import serial

class DriverInterface():
  def __init__(self):
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
    next_rand = [random.randint(0,255) for _ in range(0,16)]
    next_randstr = "e" + "".join(["%02x" % nr for nr in next_rand]) + "\n"
    self.frontend.arm()
    time.sleep(1.0)
    self.ser.write(next_randstr.encode("utf-8"))
    print("Written")
    f = self.ser.read(32)
    print("OK")
    # grab newline
    return (next_rand,[0xAA] * 16)


  def close(self):
    self.ser.close()
    pass
