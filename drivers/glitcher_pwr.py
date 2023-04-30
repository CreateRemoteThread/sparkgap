#!/usr/bin/env python3

from drivers import base
import time
import random
import serial
import sparkgap.glitcher

class DriverInterface(base.BaseDriverInterface):
  def __init__(self):
    super().__init__()
    self.config = {}
    self.config["trigger"] = None
    print("Using glitcher_pwr v2 (bridge-mode) driver")
    self.g = sparkgap.glitcher.MPDevice()
    self.g.con()
    self.g.initDefault()
    self.g.enablemux(1)
    print("OK, mux enabled")

  def init(self,scope):
    self.scope = scope
    print("glitcher_pwr v2 initialization: nothing needed")
   
  def drive(self,data_in = None):
    next_rand = [1 for _ in range(16)]
    next_autn = [1 for _ in range(16)]
    self.scope.arm()
    time.sleep(0.5)
    self.g.muxout("glitcher.SELECT_MUXA")
    time.sleep(0.5)
    self.g.muxout("glitcher.SELECT_NONE")
    return (next_rand,next_autn)

  def close(self):
    pass
