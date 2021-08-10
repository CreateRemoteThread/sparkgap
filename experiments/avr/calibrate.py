#!/usr/bin/env python3

import sys
import chipwhisperer as cw
import serial
import csv

scope = cw.scope()
scope.default_setup()
target = cw.target(scope)

# target.baud = 9600
print("Configuring UART")
target.init()

print("Entering glitch loop...")

csvfile = open("eggs.csv","w",newline='')
csvwriter = csv.writer(csvfile,delimiter=',')

# pdic hooked up to a 2n7000 reset puller
# parasitic power from UART prevents the target from resetting
# properly, so we need to force the pin

ser = serial.Serial("/dev/ttyUSB0",9600,timeout=2.0)

scope.gain.gain = 25
scope.adc.samples=3000
scope.adc.offset = 0
scope.adc.basic_mode = "rising_edge"
scope.clock.clkgen_freq = 32000000
scope.clock.adc_src = "clkgen_x4"
# scope.io.tio1 = "serial_tx"
# scope.io.tio2 = "serial_rx"
scope.trigger.triggers = "tio4"
scope.glitch.clk_src = "clkgen"
scope.glitch.output = "glitch_only"
scope.glitch.trigger_src = 'ext_single'
scope.io.glitch_hp  = True
scope.io.glitch_lp = False

# ser = serial.Serial("/dev/ttyUSB0",9600,timeout=3.0)

import random
import time

tryCount = 0

import base64

while tryCount < 1000:
  tryCount += 1
  scope.glitch.width = random.randint(5,45)
  scope.glitch.repeat = random.randint(1,5)
  scope.glitch.ext_offset = 1453
  scope.glitch.offset = random.randint(1,45)
  # :37 R:4 E:3 O:19
  scope.glitch.width = 37
  scope.glitch.repeat = 4
  # scope.glitch.ext_offset = 3
  scope.glitch.offset=19
  scope.io.pdic = True
  time.sleep(0.3)
  scope.io.target_pwr = False
  time.sleep(0.5)
  scope.io.target_pwr = True
  time.sleep(0.3)
  scope.io.pdic = False
  ser.flushInput()
  scope.arm()
  time.sleep(0.1)
  ser.write(b"1\r")
  # target.ser.write("1\r")
  output = ser.read(10)
  # output = target.ser.read(10,timeout=300)
  scope.capture()
  if b"1000000" not in output:
    print("W:%d R:%d E:%d O:%d" % (scope.glitch.width,scope.glitch.repeat,scope.glitch.ext_offset,scope.glitch.offset))
    print(output)
    csvwriter.writerow([scope.glitch.width,scope.glitch.repeat,scope.glitch.ext_offset,scope.glitch.offset,base64.b64encode(output)])
  else:
    print("+ W:%d R:%d E:%d O:%d" % (scope.glitch.width,scope.glitch.repeat,scope.glitch.ext_offset,scope.glitch.offset))
    csvwriter.writerow([scope.glitch.width,scope.glitch.repeat,scope.glitch.ext_offset,scope.glitch.offset,"E"])
  sys.stdout.flush()

# csvwriter.close()
csvfile.close()
