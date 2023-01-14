#!/usr/bin/env python3

# include library for glitcher.Glitcher (locally)

import serial
import time
import sys

class MPDevice:
  def __init__(self,port="/dev/ttyACM0"):
    self.port = port
    self.ser = None

  def con(self):
    self.ser = serial.Serial(self.port,115200)
    print("connected")

  def initDefault(self):
    self.sendCommand(b"import glitcher")
    self.sendCommand(b"g = glitcher.Glitcher()")
    self.sendCommand(b"g.setmask(glitcher.SELECT_MOSFET)")

  def enablemux(self,status):
    if status is True or status == 1:
      self.sendCommand(b"g.enablemux(True)")
    elif status is False or status == 0:
      self.sendCommand(b"g.enablemux(False)")

  def setmask(self,mask):
    self.sendCommand(b"g.setmask(%s)" % mask.encode("utf-8"))
 
  def muxout(self,muxselect):
    self.sendCommand(b"g.muxout(%s)" % muxselect.encode("utf-8"))

  def rnr(self,delay,width):
    self.sendCommand(b"g.rnr(delay=%d,width=%d)" % (delay,width))
  
  def setrepeat(self,num,delay):
    self.sendCommand(b"g.setrepeat(num=%d,delay=%d)" % (num, delay))

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
      # print(outTokens)
      return outTokens
    else:
      return None

  def dis(self):
    self.ser.close()

if __name__ == "__main__":
  print("This module is not intended to be called directly")
