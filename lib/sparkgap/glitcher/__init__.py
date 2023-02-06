#!/usr/bin/env python3

# include library for glitcher.Glitcher (locally)

import serial
import time
import sys

# so we don't have to use strings in setmask or muxout
SELECT_MOSFET = "glitcher.SELECT_MOSFET"
SELECT_MUXA = "glitcher.SELECT_MUXA"
SELECT_MUXB = "glitcher.SELECT_MUXB"
SELECT_MUXC = "glitcher.SELECT_MUXC"

class MPDevice:
  def __init__(self,port="/dev/ttyACM0"):
    self.port = port
    self.ser = None

  def con(self):
    self.ser = serial.Serial(self.port,115200)
    print("connected")

  def initDefault(self):
    self.raw(b"import glitcher")
    self.raw(b"g = glitcher.Glitcher()")
    self.raw(b"g.setmask(glitcher.SELECT_MOSFET)")

  def enablemux(self,status):
    if status is True or status == 1:
      self.raw(b"g.enablemux(True)")
    elif status is False or status == 0:
      self.raw(b"g.enablemux(False)")
  muxenable = enablemux

  def setmask(self,mask):
    self.raw(b"g.setmask(%s)" % mask.encode("utf-8"))
 
  def muxout(self,muxselect):
    self.raw(b"g.muxout(%s)" % muxselect.encode("utf-8"))

  def rnr(self,delay,width):
    self.raw(b"g.rnr(delay=%d,width=%d)" % (delay,width))
  
  def setrepeat(self,num,delay):
    self.raw(b"g.setrepeat(num=%d,delay=%d)" % (num, delay))

  # lol what the shit...
  def raw(self,cmd,waitResp=True,waitTime=0.1):
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
