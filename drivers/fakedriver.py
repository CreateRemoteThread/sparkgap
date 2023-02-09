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
    print("Using fakedriver")

  def init(self,scope):
    self.scope = scope
   
  def drive(self,data_in = None):
    next_rand = [1 for _ in range(16)]
    next_autn = [1 for _ in range(16)]
    self.scope.arm()
    input(" armed, hit any key to continue... >")
    return (next_rand,next_autn)

  def close(self):
    pass
