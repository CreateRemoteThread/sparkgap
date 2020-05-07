#!/usr/bin/env python3

import time
import logging
import os
from collections import namedtuple
import csv
import serial
import random

import numpy as np
import sys

import chipwhisperer as cw
logging.basicConfig(level=logging.WARN)
scope= cw.scope()
target = cw.target(scope)

scope.adc.samples = 3000
scope.adc.offset = 0
scope.adc.basic_mode = "rising_edge"
scope.clock.clkgen_freq = 120000000 # 7370000
scope.clock.adc_src = "clkgen_x1"
scope.io.tio1 = "serial_rx"
scope.io.tio2 = "serial_tx"
scope.trigger.triggers = "tio4"
scope.glitch.clk_src = "clkgen"
scope.glitch.output = "enable_only"
scope.io.glitch_lp = False
scope.io.glitch_hp = True
target.go_cmd = ""
target.key_cmd = ""

print(scope.clock.clkgen_freq)

scope.glitch.trigger_src = 'ext_single'
print("OK, go")

scope.glitch.offset = 45
scope.glitch.width = 45
scope.glitch.repeat = 165
# scope.glitch.repeat = 235
scope.glitch.ext_offset =5

target.baud = 115200
target.init()

scope.io.pdic = "low"

ser = serial.Serial("/dev/ttyUSB0",baudrate=115200)

CONFIG_DO_RESET = True
for arg in sys.argv[1:]:
  if arg == "--no-reset":
    print("Option: do not reset")
    CONFIG_DO_RESET = False

def resetDevice():
  scope.io.pdic = "high"
  time.sleep(0.3)
  scope.io.pdic = "low"

def doLogin():
  ser.timeout = 180 # easier to push past pi@[undervoltage]raspberrypi
  print("Waiting for login...")
  ser.read_until(b"raspberrypi login")
  ser.write(b"pi\n")
  ser.timeout = 30
  print("Waiting for password...")
  ser.read_until(b"Password:")
  ser.write(b"raspberry\n")
  print("Waiting for shell...")
  ser.read_until(b"$")
  ser.timeout = None

ser.flush()
if CONFIG_DO_RESET:
  resetDevice()
  doLogin()

#5 is earliest
#850 is the latest

import base64
f = open("log.csv","w")

glitchBrute = 0

tryme = 0

while scope.glitch.ext_offset < 850:
  if tryme == 10:
    tryme = 0
    scope.glitch.ext_offset += 7
  else:
    tryme += 1
  scope.glitch.repeat = random.randint(165,235)
  print("Glitching @ %d (%d repeat)" % (scope.glitch.ext_offset,scope.glitch.repeat))
  ser.flush()
  scope.arm()
  ser.write(b"./bonk\n")
  timeout = 100000
  while target.isDone() is False and timeout > 0:
    timeout -= 1
    time.sleep(0.01)
  # try:
  #   scope.capture()
  # except:
  #   pass
  ser.timeout = 0.5
  d = ser.read(1024)
  print(d)
  ser.timeout = None
  if b"6250000" not in d and b"pi@raspberry" in d:
    print("Op success.")
    scope.dis()
    target.dis()
    sys.exit(0)
  elif b"pi@raspberry" in d:
    print("No reset")
    pass
  else:
    print("Resetting device")
    ser.flush()
    resetDevice()
    doLogin()
  f.write("%d,%s\n" % (scope.glitch.ext_offset,base64.b64encode(d)))

f.close()
scope.dis()
target.dis()
sys.exit(0)

