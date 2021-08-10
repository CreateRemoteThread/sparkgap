#!/usr/bin/env python3

# new calibrator for new max4619

import chipwhisperer as cw
import time
import random
import serial
import sys

scope = cw.scope()
target = cw.target(scope)

scope.clock.clkgen_freq = 32000000
scope.clock.adc_src = "clkgen_x1"
scope.glitch.clk_src = "clkgen"
scope.glitch.output = "glitch_only"
scope.trigger.triggers = "tio4"
scope.glitch.trigger_src = "ext_single"

if len(sys.argv) != 3:
  print("./hulksmash.py [csv] [try_count]")
  sys.exit(0)
f = open(sys.argv[1],"w")

scope.glitch.offset=30
scope.glitch.width=40
scope.glitch.repeat=1
scope.io.glitch_hp = True

scope.io.target_pwr = False
time.sleep(0.2)
print("Starting!")

ser = serial.Serial("/dev/ttyUSB0",9600,timeout=1.5)
import base64
f.write("Repeat,Width,Offset,Ext_Offset")
f.write("\n")
for attempt in range(0,int(sys.argv[2])):
  scope.glitch.offset = random.randint(35,45)
  scope.glitch.width = random.randint(25,45)
  scope.glitch.repeat = random.randint(5,15)
  scope.glitch.ext_offset = random.randint(0,60)
  scope.arm()
  ser.flushInput()
  scope.io.target_pwr = True
  output = ser.read(30)
  scope.capture()
  f.write("%d,%d,%d,%d,%s" % (scope.glitch.repeat, scope.glitch.width,scope.glitch.offset ,scope.glitch.ext_offset,base64.b64encode(output).decode("utf-8")))
  f.write("\n")
  print("#:%d R:%d E:%d W:%d O:%d: %s" % (attempt,scope.glitch.repeat,scope.glitch.ext_offset,scope.glitch.width,scope.glitch.offset,output)) 
  scope.io.target_pwr = False
  time.sleep(0.2)

f.close()
