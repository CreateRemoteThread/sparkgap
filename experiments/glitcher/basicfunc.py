#!/usr/bin/env python3

# Physical test case:
# - X output, 2x30R to VCC pad of AVR target
# - TRIG_IN pad to TRIG_IN on glitcher
# - GL_OUT to AVR VCC + GND

import serial
import time

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
      # print(outTokens)
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

import random

# results:

# delay = (80,90), (130,150)
# w=3
# 5 repeats, delay 1
# seems to caues shortening of the loop (but fw bug = last good result)

validOut = 0
resetOut = 0
for i in range(1,100):
  # de = random.randint(10,20)
  de = random.randint(5,15)
  w = 7
  print("delay %d:width %d" % (de,w))
  mp.sendCommand(b"g.setrepeat(num=2,delay=9)")
  print("Switching on")
  mp.sendCommand(b"g.muxout(glitcher.SELECT_MUXA)") # off
  td.ser.flush()
  time.sleep(0.1)
  mp.sendCommand(b"g.rnr(delay=%d,width=%d)" % (de,w))
  time.sleep(0.1)
  while td.ser.inWaiting():
    td.ser.read()
  d = td.fire()
  print(d)
  if d == b'62500\r\n':
    validOut += 1
  elif d == b'hello\r\n':
    resetOut += 1
  elif d == b'':
    print("Skip exit")
    resetOut += 1
  else:
    time.sleep(5.0)
    print("WAiting for mega loop")
    while td.ser.inWaiting():
      dx = td.ser.read()
    print(dx)
    sys.exit(0)
  td.ser.flush()
  time.sleep(1.0)
  print("Switching off")
  mp.sendCommand(b"g.muxout(glitcher.SELECT_NONE)") # on

print("exiting, valid %d, reset %d" % (validOut,resetOut)) 
 
td.dis()
mp.dis()
