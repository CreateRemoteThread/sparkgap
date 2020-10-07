#!/usr/bin/env python3

import time
import sys
import serial

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
    # print("Writing!")
    # print(cmdstr)
    self.ser.write(cmdstr)
    x = self.fetchUntil(">")
    for l in "".join(x).split("\n"):
      if "READ" in l:
        out +=  [int(l.split(" ")[3],16)]
    return out

if __name__ == "__main__":
  bp = BuspirateSPI()
  bp.beginSPI()
  for x in range(0,0x100):
    for y in range(0,0x100):
      f = bp.command(b"{0xac,A,0x53,0x00,0x00,0x50,0x%02x,0x%02x,0x00,0x20,0x00,0x00,0x00]a\n" % (x,y))
      time.sleep(0.05)
      outstr = "".join(["%02x" % xl for xl in f])
      print("%02x:%02x:%s" % (x,y,outstr))
      sys.stdout.flush()
