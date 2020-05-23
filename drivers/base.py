#!/usr/bin/env python3

import random

class BaseDriverInterface:
  def __init__(self):
    self.config = {}

  def init(self):
    print("BaseDriverInterface: init() called")
    pass

  def drive(self,in_text=None):
    print("BaseDriverInterface: drive() called")
    if in_text is None:
      r_in   = [random.randint(0,255) for i in range(0,16)]
      r_out  = [random.randint(0,255) for i in range(0,16)]
      return (r_in,r_out)
    else:
      r_out  = [random.randint(0,255) for i in range(0,len(r_in))]
      return (r_in,r_out)

  def close(self):
    print("BaseDriverInterface: close() called")
    pass


