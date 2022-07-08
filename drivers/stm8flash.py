#!/usr/bin/env python3

from drivers import base
import chipwhisperer as cw
import subprocess
import random
import time

# Using github.com vdudouyt/stm8flash
STM8FLASH_PATH = "/home/test/software/stm8flash/stm8flash"

class DriverInterface(base.BaseDriverInterface):
  def __init__(self):
    super().__init__()
    self.config = {}
    print("Using STM8Flash driver")
    self.scope = cw.scope()
    self.target = cw.target(self.scope)
    self.scope.io.target_pwr = False
    self.scope.io.pdic = "high"
    GLITCH_SETUP = True
    if GLITCH_SETUP:
      self.scope.gain.gain = 25
      self.scope.adc.samples=3000
      self.scope.adc.offset = 0
      self.scope.adc.basic_mode = "falling_edge"
      self.scope.clock.clkgen_freq = 80000000
      self.scope.clock.adc_src = "clkgen_x4"
      self.scope.trigger.triggers = "tio4"
      self.scope.glitch.clk_src = "clkgen"
      self.scope.glitch.output = "enable_only"
      self.scope.glitch.trigger_src = 'ext_single'
      self.scope.io.glitch_hp  = True
      self.scope.io.glitch_lp = False

  def init(self,frontend=None):
    self.frontend = frontend
    pass

  def drive(self,in_text=None):
    self.scope.glitch.width=10
    self.scope.glitch.ext_offset = 45000
    self.scope.glitch.repeat = 10
    self.scope.glitch.width = 10
    self.scope.glitch.offset = 5
    self.scope.arm()
    next_rand = [0x00 for _ in range(0,16)]
    self.frontend.arm()
    time.sleep(0.5)
    self.scope.io.target_pwr = True
    time.sleep(0.25)
    self.scope.io.pdic = "low"
    p = subprocess.Popen([STM8FLASH_PATH,"-c","stlinkv2","-p","stm8l001j3","-r","/tmp/bonk.bin"])
    (data_out,data_err) = p.communicate()
    self.scope.io.pdic = "high"
    print("OK!")
    self.scope.io.target_pwr = False
    self.scope.capture()
    return (next_rand,next_rand)

  def close(self):
    self.target.dis()
    self.scope.dis()
    pass
