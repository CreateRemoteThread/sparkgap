#!/usr/bin/env python3

from drivers import base
import time
import random
import serial
import sparkgap.glitcher

class DriverInterface(base.BaseDriverInterface):
  def __init__(self):
    super().__init__()
    self.config = {}
    self.config["trigger"] = None
    print("Using glitcher_rst")
    self.ser = serial.Serial("/dev/ttyACM0",115200)
    self.ser.write(b"from machine import Pin\r")
    self.ser.write(b"import glitcher\r")
    self.ser.write(b"g = glitcher.Glitcher()\r")
    self.ser.write(b"g.enablemux(True)\r")
    self.ser.write(b"g.muxout(glitcher.SELECT_MUXA)\r")
    self.ser.write(b"cs = Pin(14,Pin.OUT)\r")
    self.ser.write(b"cs.value(1)\r")
    # input(">")
    time.sleep(0.25)
    out = b""
    dc = self.ser.inWaiting()
    while dc != 0:
      out += self.ser.read(dc)
      time.sleep(0.1)
      dc = self.ser.inWaiting()
    print(out)
    print("OK, RST currently high")

  def init(self,scope):
    self.scope = scope
    print("default initialization")
   
  def drive(self,data_in = None):
    next_rand = [1 for _ in range(16)]
    next_autn = [1 for _ in range(16)]
    self.scope.arm()
    # input(">")
    time.sleep(0.25)
    self.ser.write(b"cs.value(0)\r")
    time.sleep(0.5)
    self.ser.write(b"cs.value(1)\r")
    time.sleep(0.25)
    out = b""
    dc = self.ser.inWaiting()
    while dc != 0:
      out += self.ser.read(dc)
      time.sleep(0.1)
      dc = self.ser.inWaiting()
    print(out)
    return (next_rand,next_autn)

  def close(self):
    pass
