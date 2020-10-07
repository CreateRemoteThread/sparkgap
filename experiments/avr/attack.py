#!/usr/bin/env python3

import sys
import chipwhisperer as cw
import serial
import csv

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

scope = cw.scope()
scope.default_setup()
target = cw.target(scope)

print("Configuring UART")
target.init()

print("Entering glitch loop (attack ver)")
import uuid

# csvfile = open("eggs-%s.csv" % uuid.uuid4(),"w",newline='')
# csvwriter = csv.writer(csvfile,delimiter=',')

scope.gain.gain = 25
scope.adc.samples=3000
scope.adc.offset = 0
scope.adc.basic_mode = "rising_edge"
scope.clock.clkgen_freq = 80000000
scope.clock.adc_src = "clkgen_x4"
# scope.io.tio1 = "serial_tx"
# scope.io.tio2 = "serial_rx"
scope.trigger.triggers = "tio4"
scope.glitch.clk_src = "clkgen"
scope.glitch.output = "enable_only"
scope.glitch.trigger_src = 'ext_single'
scope.io.glitch_hp  = True
scope.io.glitch_lp = False

# ser = serial.Serial("/dev/ttyUSB0",9600,timeout=3.0)

import random
import time

tryCount = 0

import base64

bp = BuspirateSPI()
bp.beginSPI()

while tryCount < 1000:
  time.sleep(0.5)
  tryCount += 1
  scope.glitch.width = random.randint(5,45)
  scope.glitch.repeat = random.randint(1,5)
  scope.glitch.ext_offset = 146850
  # scope.glitch.ext_offset = 136850
  scope.glitch.offset = random.randint(1,45)
  # :37 R:4 E:3 O:19
  scope.glitch.width = 37
  scope.glitch.repeat = 4
  scope.glitch.ext_offset += random.randint(-100,100)
  # scope.glitch.ext_offset = 3
  scope.glitch.offset=19
  scope.arm()
  time.sleep(0.1)
  print("E: %d" % scope.glitch.ext_offset)
  cmd = b"{0xac,0x53,0x11,A,0x22,0x20,0x00,0x00,0xAA,0x28,0x00,0x00,0xAA]a\n"
  x = bp.command(cmd)
  print(["%02x" % xp for xp in x])
  scope.capture()
  sys.stdout.flush()

