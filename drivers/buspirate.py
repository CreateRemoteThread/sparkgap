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
    out = []
    while c != waitChar:
      c = self.ser.read(1).decode("utf-8")
      out.append(c)
    return out

  def init(self,frontend=None):
    print("initializing uart")
    self.ser = serial.Serial("/dev/ttyUSB0",115200)
    self._resetInitSPI()
    self.frontend = frontend

  def _resetInitSPI(self):
    self.ser.write(b"#\n")
    time.sleep(0.25)
    self.fetchUntil(">")
    print("Starting configuration")
    self.ser.write(b"m5\n")
    self.fetchUntil(">")
    print("Selected SPI mode")
    self.ser.write(b"4\n") # 1MHz. 1 is 30KHz if we need
    self.fetchUntil(">")
    print("Selected 1MHz")
    self.ser.write(b"1\n") # idle low
    self.fetchUntil(">")
    print("Selected Idle Low")
    self.ser.write(b"2\n") # output clk edge (default)
    self.fetchUntil(">")
    print("Selected clk edge default")
    self.ser.write(b"1\n") # sample mid
    self.fetchUntil(">")
    print("Selected sample at mid-clk")
    self.ser.write(b"2\n") # /CS (instead of CS)
    self.fetchUntil(">")
    print("Selected /CS")
    self.ser.write(b"2\n") # push pull (vs open drain)
    self.fetchUntil(">")
    print("OK!")

  def drive(self,in_text=None):
    self._resetInitSPI()
    self.frontend.arm()
    time.sleep(0.5)
    # self.ser.write(b"{A,0xac,0x52,a,0xac,0x22,0x20,0x00,0x00,0xAA,0x28,0x00,0x00,0xAA]a\n")
    self.ser.write(b"{A,0xac,0x53,a,0x11,0x22,0x20,0x00,0x00,0xAA,0x28,0x00,0x00,0xAA]a\n")
    # self.ser.write(b"{0xac,0x53,0x11,0x22,0xac,A,0xff,a,0x00,0xAA]a\n")
    x = self.fetchUntil(">")
    print("".join(x))
    return ([0x00] * 16,[0xaa] * 16)

  def close(self):
    try:
      self.ser.close()
    except:
      pass


