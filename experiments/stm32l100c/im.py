#!/usr/bin/env python3

import sys
import chipwhisperer as cw
import time
import random
import chipshouter

scope = None
target = None
# ext_single

cs = None

def initAll():
  print("Configuring CW")
  global scope, target,cs
  scope = cw.scope()
  target = cw.target(scope)
  scope.adc.samples = 5000
  scope.adc.offset = 0
  scope.adc.basic_mode = "rising_edge"
  scope.clock.clkgen_freq = 8000000 # 120000000 # 737060
  scope.clock.adc_src = "clkgen_x1"
  scope.trigger.triggers = "tio4"
  scope.io.hs2 = "glitch"
  scope.glitch.clk_src = "clkgen"
  scope.glitch.output = "enable_only"
  scope.io.glitch_lp = False
  scope.io.glitch_hp = True
  scope.glitch.trigger_src = 'ext_single'
  print("Configuring CS")
  cs = chipshouter.ChipSHOUTER("/dev/ttyUSB0")
  cs.reset_config = True
  cs.voltage = 350
  cs.clr_armed = True

initAll()
trycounter = 0
CONFIG_TRY = 25

print("Target init")
target.init()
scope.io.target_pwr = False
trycounter = 0 # change CONFIG_TRY you fucking idiot
time.sleep(5.0)

print(cs)

print("Go!")
while trycounter < CONFIG_TRY:
  if cs.trigger_safe == False:
    print("Unsafe to trigger. Waiting 5 seconds grace period")
    time.sleep(5.0)
    if cs.trigger_safe == False:
      print("Unsafe to trigger. Exiting")
      cs.armed = False
      print(cs)
      target.dis()
      scope.dis()
      sys.exit(0)
  scope.glitch.width = 8
  scope.glitch.repeat = 1
  scope.glitch.offset = 5
  scope.glitch.ext_offset = 100
  scope.arm()
  time.sleep(0.1)
  scope.io.target_pwr = True
  f = scope.capture()
  # scope.glitch.cwg.glitchManual()
  time.sleep(0.5)
  scope.io.target_pwr = False
  time.sleep(2.0)
  print("%d Glitched, reps %d" % (trycounter,1))
  trycounter += 1



cs.armed = False
print("Disarmed...")
print(cs)
target.dis()
scope.dis()

print("Bye!")

