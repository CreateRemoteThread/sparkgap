#!/usr/bin/env python3

import serial
import time

class TargetDevice:
  def __init__(self):
    self.ser = None
    pass

  def con(self):
    self.ser = serial.Serial("/dev/ttyUSB0",9600)
    # self.ser.read()

  def dis(self):
    self.ser.close()

  def fire(self):
    self.ser.write(b"e")
    time.sleep(0.1)
    out = b""
    while self.ser.inWaiting():
      out += self.ser.read()
    return out

class MPDevice:
  def __init__(self,port="/dev/ttyACM0"):
    self.port = port
    self.ser = None

  def con(self):
    self.ser = serial.Serial(self.port,115200)
    print("connected")

  # lol what the shit...
  def sendCommand(self,cmd,waitResp=True,waitTime=0.1):
    self.ser.write(cmd + b"\r")
    if waitTime is not None:
      time.sleep(waitTime)
    if waitResp:
      out = b""
      while self.ser.inWaiting():
        out += self.ser.read()
      outTokens = out.split(b"\r\n")
      if b"Traceback" in out:
        print(outTokens)
      return outTokens
    else:
      return None

  def dis(self):
    self.ser.close()

import sys

td = TargetDevice()
td.con()
print(td.fire())
print(td.fire())

mp = MPDevice()
mp.con()
mp.sendCommand(b"import glitcher")
mp.sendCommand(b"g = glitcher.Glitcher()")
mp.sendCommand(b"g.setmask(glitcher.SELECT_MOSFET)")
mp.sendCommand(b"g.enablemux(True)")

for i in range(110,130):
  de = i
  mp.sendCommand(b"g.setrepeat(num=2,delay=9)")
  mp.sendCommand(b"g.rnr(delay=%d,width=7)" % de)
  print("Switching on")
  mp.sendCommand(b"g.muxout(glitcher.SELECT_MUXA)") # off
  print(td.fire())
  time.sleep(1.0)
  print("Switching off")
  mp.sendCommand(b"g.muxout(glitcher.SELECT_NONE)") # on
  
td.dis()
mp.dis()
