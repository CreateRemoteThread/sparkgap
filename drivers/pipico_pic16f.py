#!/usr/bin/env python3

from drivers import base
import random
import time
import mpremote
from mpremote.main import State
from mpremote.commands import _do_execbuffer,do_soft_reset

class DriverInterface(base.BaseDriverInterface):
  def __init__(self):
    super().__init__()
    self.config = {}
    print("Using mpremote driver for pic16f")
    pass

  def init(self,frontend=None):
    print("initializing mpremote, resetting target")
    self.frontend = frontend
    self.s = State()
    do_soft_reset(self.s)
    _do_execbuffer(self.s,"import pic_gpio",True)
    pass

  def drive(self,in_text=None):
    self.frontend.arm()
    time.sleep(0.1)
    _do_execbuffer(self.s,"pic_gpio.triggerOnReset()",True)
    return ("0","0")

  def close(self):
    do_soft_reset(self.s)
    pass
