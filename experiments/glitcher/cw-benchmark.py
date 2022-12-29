#!/usr/bin/env python3

import chipwhisperer as cw
import serial
import time
import sys

scope = None
target = None

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

def initAll():
  global scope, target
  scope = cw.scope()
  target = cw.target(scope)
  scope.adc.samples = 3000
  scope.adc.offset = 0
  scope.adc.basic_mode = "rising_edge"
  scope.clock.clkgen_freq = 120000000 # 120000000 # 7370000
  scope.clock.adc_src = "clkgen_x1"
  scope.trigger.triggers = "tio4"
  scope.glitch.clk_src = "clkgen"
  scope.glitch.output = "enable_only"
  # scope.glitch.output = "glitch_only"
  scope.io.glitch_lp = True
  scope.io.glitch_hp = False
  target.go_cmd = ""
  target.key_cmd = ""
  scope.glitch.trigger_src = 'ext_single'
  scope.io.target_pwr = False

import random
td = TargetDevice()
initAll()
td.con()
td.flush()
for i in range(0,1000):
  print("Firing!")
  scope.io.target_pwr = True
  scope.glitch.width=1 # doesn't matter for enable_only
  scope.glitch.repeat=random.randint(1,5)
  scope.glitch.ext_offset=random.randint(1,500)
  time.sleep(0.25)
  scope.arm()
  d = td.fire()
  print(b"GREP E:%d R:%d: " % (scope.glitch.ext_offset,scope.glitch.repeat) + d)
  time.sleep(0.25)
  scope.io.target_pwr = False
  time.sleep(0.5)
  sys.stdout.flush()

target.dis()
scope.dis()
td.dis()

