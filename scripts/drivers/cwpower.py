#!/usr/bin/env python3

from drivers import base
import chipwhisperer as cw
# import random
import time

class DriverInterface(base.BaseDriverInterface):
  def __init__(self):
    super().__init__()
    self.config = {}
    self.config["trigger"] = None
    print("Using cw-power driver: good hunting")
    self.cw = cw.scope()
    self.target = cw.target(self.cw)
    self.cw.default_setup() # don't care
    self.cw.io.target_pwr = False

  def init(self,scope):
    print("cw-power initialization: nothing needed")
   
  def drive(self,data_in = None):
    next_rand = [1 for _ in range(16)]
    next_autn = [1 for _ in range(16)]
    self.cw.io.target_pwr = True
    time.sleep(1.0)
    self.cw.io.target_pwr = False
    return (next_rand,next_autn)

  def close(self):
    pass
