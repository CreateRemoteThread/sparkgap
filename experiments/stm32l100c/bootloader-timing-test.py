#!/usr/bin/env python3

import sys
import chipwhisperer as cw
import time
import random

# from reset, 27000 -> ~40000 @ 8mhz clock

scope = None
target = None

def initCw():
  global scope,target
  print("Configuring ChipWhisperer")
  scope = cw.scope()
  target = cw.target(scope)
  # scope.default_setup()
  scope.adc.samples = 5000
  scope.adc.offset = 0
  scope.adc.basic_mode = "rising_edge"
  scope.clock.clkgen_freq = 8000000 # 120000000 # 737060
  scope.clock.clkgen_src = "system"
  scope.clock.adc_src = "clkgen_x1"
  scope.trigger.triggers = "tio4"
  scope.glitch.clk_src = "clkgen"
  scope.glitch.output = "enable_only"
  scope.io.glitch_lp = False
  scope.io.glitch_hp = True
  print(scope.adc.state)
  scope.io.hs2 = "glitch"
  scope.glitch.trigger_src = 'ext_single'

initCw()
scope.io.target_pwr = False

scope.glitch.width = 30
scope.glitch.repeat = 4
scope.glitch.offset = 20
scope.glitch.ext_offset = 27000
target.init()
time.sleep(0.5)
print(scope)
input(">")
print("Arm and capture!")
scope.arm()
scope.io.target_pwr = True
# f = scope.capture()
time.sleep(3.0)

print("Disabling target...")

scope.io.target_pwr = False
target.dis()
scope.dis()

