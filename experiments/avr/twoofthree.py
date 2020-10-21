#!/usr/bin/env python3

# clock glitch variant

import sys
import chipwhisperer as cw
import serial
import csv

class AvrSpecial:
  def __init__(self):
    self.ser = serial.Serial("/dev/ttyUSB0",9600,timeout=2.0)

  def drive(self,in_text=None):
    time.sleep(0.5)
    self.ser.write(b"#\x08\xFF\xAC\x00\x53\x00\x00\x00\x00\x00\x20\x00\x00\x00\x00\x00\xFF#")
    x = self.ser.read(1)
    if x != b'#':
      print("Critical Error: expected '#', got ",)
      print(x)
    x = self.ser.read(8)
    if x[2:] != b"\x53\x00\x00\x20\x00\xff":
      print(["%02x" % ix for ix in x])
      print("Success, EEPROM corrupted")
      input(">")
      sys.exit(0)
    # ['ff', 'ff', '53', '00', '00', '20', '00', 'ff']
    print(["%02x" % ix for ix in x])
    return x[-1]

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
scope.adc.basic_mode = "falling_edge"
scope.clock.clkgen_freq = 16000000
scope.clock.adc_src = "clkgen_x4"
scope.trigger.triggers = "tio4"
scope.glitch.clk_src = "clkgen"
scope.glitch.output = "clock_or"
scope.glitch.trigger_src = 'ext_single'
scope.io.hs2 = "glitch"
scope.io.glitch_hp  = False
scope.io.glitch_lp = False

# ser = serial.Serial("/dev/ttyUSB0",9600,timeout=3.0)

import random
import time

tryCount = 0

import base64

bp = AvrSpecial()
while tryCount < 2000:
  time.sleep(0.5)
  tryCount += 1
  scope.glitch.offset = random.randint(1,45)
  # scope.glitch.width = random.randint(1,45)
  scope.glitch.width = 30
  scope.glitch.offset = 37
  scope.glitch.repeat = random.randint(1,100)
  #scope.glitch.ext_offset = 894 + random.randint(-15,15)
  scope.glitch.ext_offset = 1 + random.randint(0,30)
  # scope.glitch.ext_offset = 3984 + random.randint(-50,50)

  # scope.glitch.ext_offset = 
  # scope.glitch.offset=19
  scope.arm()
  time.sleep(0.1)
  print("E:%d, R:%d, W:%d, O:%d" % (scope.glitch.ext_offset,scope.glitch.repeat,scope.glitch.width,scope.glitch.offset))
  x = bp.drive()
  print(x)
  if x != 0xFF:
    print("Success, EEPROM corruption\n")
    target.dis()
    scope.dis()
    sys.exit(0)
  scope.capture()
  sys.stdout.flush()

