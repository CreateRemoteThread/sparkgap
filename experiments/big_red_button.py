#!/usr/bin/env python3

import chipwhisperer as cw
import time
import random

scope = cw.scope()
target = cw.target(scope)

scope.clock.clkgen_freq = 16000000
scope.clock.adc_src = "clkgen_x1"
scope.glitch.clk_src = "clkgen"
scope.glitch.output = "glitch_only"

scope.glitch.offset=30
scope.glitch.width=40
scope.glitch.repeat=1
scope.io.glitch_hp = True
scope.glitch.trigger_src = "manual"

scope.io.target_pwr = True

while True:
  x = input("> ")
  if x.rstrip() == "q":
    print("ok")
    break
  elif x.rstrip() == "r":
    for i in range(0,10):
      print("Glitching %d" % i)
      scope.glitch.manual_trigger()
      # time.sleep(0.1)     
  else:
    glen = int(x.rstrip())
    print("Glitching %d" % glen)
    scope.glitch.repeat = glen
    scope.glitch.manual_trigger()

scope.io.target_pwr = False
