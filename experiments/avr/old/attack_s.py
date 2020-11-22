#!/usr/bin/env python3

import time
import sys
import serial
import chipwhisperer as cw

class BuspirateSPI:
  def __init__(self):
    self.ser = serial.Serial("/dev/ttyUSB0",115200,timeout=2.0)
  
  def fetchUntil(self,waitChar):
    c = None
    out = []
    while c != waitChar:
      c = self.ser.read(1).decode("utf-8")
      out.append(c)
    # out.append(c)
    return out

  def beginSPI(self):
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

  def command(self,cmdstr):
    out = []
    self.ser.write(cmdstr)
    x = self.fetchUntil(">")
    for l in "".join(x).split("\n"):
      if "READ" in l:
        # print(l.split(" "))
        out +=  [int(l.split(" ")[3],16)]
    print(["%02x" % o for o in out])
    return out

if __name__ == "__main__":
  bp = BuspirateSPI()
  bp.beginSPI()
  bp.command(b"{0xac,A,0x53,0x11,0x22,0x20,0x00,0x00,0xAA,0x28,0x00,0x00,0xAA]a\n")
