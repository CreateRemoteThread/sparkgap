#!/usr/bin/env python3

import sys
import logging
import chipwhisperer as cw
import time
import random

print("Configuring CW")
logging.basicConfig(level = logging.WARN)

scope = None
target = None
# ext_single

def initAll():
  global scope, target
  scope = cw.scope()
  target = cw.target(scope)
  scope.adc.samples = 5000
  scope.adc.offset = 0
  scope.adc.basic_mode = "rising_edge"
  scope.clock.clkgen_freq = 64000000 # 120000000 # 7370000
  scope.clock.adc_src = "clkgen_x4"
  scope.trigger.triggers = "tio4"
  scope.glitch.clk_src = "clkgen"
  # scope.glitch.output = "enable_only"
  scope.glitch.output = "glitch_only"
  scope.io.glitch_lp = False
  scope.io.glitch_hp = True
  scope.glitch.trigger_src = 'ext_single'
  scope.adc.basic_mode = "rising_edge"
  # scope.adc.timeout = 5

initAll()
trycounter = 0
CONFIG_TRY = 50

print("Target init")
target.init()
trycounter = 0

print("Go!")
while trycounter < CONFIG_TRY:
  scope.glitch.width = random.randint(3,8)
  scope.glitch.repeat = random.randint(1,5)
  scope.glitch.offset = random.randint(-45,45)
  scope.glitch.ext_offset = random.randint(30,50)
  scope.arm()
  f = scope.capture()
  if f:
    print(f)
  print("%d Glitched, reps %d" % (trycounter,1))
  trycounter += 1

target.dis()
scope.dis()

print("Bye!")

