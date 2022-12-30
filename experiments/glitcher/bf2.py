#!/usr/bin/env python3

# Physical test case:
# - X output, 2x30R to VCC pad of AVR target
# - TRIG_IN pad to TRIG_IN on glitcher
# - GL_OUT to AVR VCC + GND

import serial
import time
import sys
import random

class TargetDevice:
  def __init__(self):
    self.ser = None
    pass

  def con(self):
    self.ser = serial.Serial("/dev/ttyUSB0",9600)
    self.ser.flush()

  def flush(self):
    self.ser.flush()

  def dis(self):
    self.ser.close()

  def fire(self):
    self.ser.write(b"c\n")
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

import sys

td = TargetDevice()
td.con()
# print(td.fire())
# print(td.fire())

mp = MPDevice()
mp.con()
mp.initDefault()
mp.enablemux(True)

# delay = (80,90), (130,150)
# w=3
# 5 repeats, delay 1
# seems to caues shortening of the loop (but fw bug = last good result)
# 94 / 96

validOut = 0
resetOut = 0
for i in range(1,100):
  # de = random.randint(10,20)
  de = random.randint(1,15)
  w = 3
  # print("delay %d:width %d" % (de,w))
  mp.setrepeat(num=5,delay=1)
  # print("Switching on")
  mp.muxout("glitcher.SELECT_MUXA")
  td.ser.flush()
  time.sleep(0.1)
  mp.rnr(delay=de,width=w)
  time.sleep(0.1)
  while td.ser.inWaiting():
    td.ser.read()
  d = td.fire()
  print(b"e:%d w:%d " % (de,w) + d)
  if d == b'62500\r\n':
    validOut += 1
  elif d == b'hello\r\n':
    resetOut += 1
  elif d == b'':
    print("Skip exit")
    resetOut += 1
  else:
    pass
    # sys.exit(0)
  td.ser.flush()
  time.sleep(1.0)
  mp.muxout("glitcher.SELECT_NONE")

print("exiting, valid %d, reset %d" % (validOut,resetOut)) 
 
td.dis()
mp.dis()
