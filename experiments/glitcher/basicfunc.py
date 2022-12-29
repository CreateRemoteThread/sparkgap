#!/usr/bin/env python3

import serial
import time

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

mp = MPDevice()
mp.con()
mp.sendCommand(b"import glitcher")
mp.sendCommand(b"g = glitcher.Glitcher()")
mp.sendCommand(b"g.setmask(glitcher.SELECT_MOSFET)")
mp.sendCommand(b"g.enablemux(True)")
print("Switching off")
mp.sendCommand(b"g.muxout(glitcher.SELECT_MUXA)") # off
print("Switching on")
time.sleep(0.1)
mp.sendCommand(b"g.muxout(glitcher.SELECT_MUXB)") # on
print("Switching off")
time.sleep(0.1)
mp.sendCommand(b"g.muxout(glitcher.SELECT_MUXA)") # off
time.sleep(1.0)

# for i in range(110,130):
#   de = i
#   mp.sendCommand(b"g.setrepeat(num=2,delay=9)")
#   mp.sendCommand(b"g.rnr(delay=de,width=7)")

print(mp.sendCommand(b"mp.writeOutput()",waitTime=0.25))
mp.dis()
