#!/usr/bin/env python3

import chipwhisperer as cw

scope = cw.scope()
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

scope.glitch.offset = 45
scope.glitch.width = 45
scope.glitch.repeat = 165
scope.glitch.ext_offset =5

print(scope.clock.clkgen_freq)

target.init()

scope.glitch.trigger_src = 'manual'
while True:
  x = input(" > ").rstrip().upper()
  if x == "Q":
    print("Bye!")
    scope.dis()
    target.dis()
    sys.exit(0)
  elif x == "G":
    scope.arm()
    timeout = 100000
    while target.isDone() is False and timeout > 0:
      timeout -= 1
      time.sleep(0.01)
