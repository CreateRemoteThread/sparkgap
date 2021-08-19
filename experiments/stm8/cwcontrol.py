#!/usr/bin/env python3

import sys
import chipwhisperer as cw

scope = cw.scope()
scope.io.pdic = False

while True:
  x = input(" > ").rstrip()
  if x == "v":
    print("Turning power on")
    scope.io.target_pwr = True
  elif x == "i":
    print("Enabling SWIM IO port")
    scope.io.pdic = True
    # scope.io.tio1 = "gpio_high"
  elif x == "o":
    print("Disabling SWIM IO port")
    scope.io.pdic = False
    # scope.io.tio1 = "gpio_low"
  elif x == "n":
    print("Turning power off")
    scope.io.target_pwr = False
  elif x in ("q","quit","Q"):
    scope.dis()
    break
