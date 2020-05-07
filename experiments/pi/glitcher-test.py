#!/usr/bin/env python3

# glitch shape calibration script

import time
import logging
import os
from collections import namedtuple
import csv
import serial

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
scope.glitch.repeat = 205
scope.glitch.ext_offset =35

target.baud = 115200
target.init()

scope.io.pdic = "low"

# resetDevice()
# doLogin()

#5 is earliest
#850 is the latest

# import base64
# f = open("log.csv","w")

attempt = 0
while True:
  print("Go! %d" % attempt)
  attempt += 1
  scope.arm()
  timeout = 10000
  while target.isDone() is False and timeout:
    timeout -= 1
    time.sleep(0.01)
  try:
    ret = scope.capture()
  except:
    pass
  #f.write("%d,%s\n" % (scope.glitch.ext_offset,base64.b64encode(d)))

# f.close()
scope.dis()
target.dis()
sys.exit(0)

