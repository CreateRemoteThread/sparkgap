#!/usr/bin/env python3

import sys
import numpy as np

class CaptureInterface():
  def __init__(self):
    self.config = {}
    self.config["samplecount"] = 5000
    print("Acquisition frontend ready")

  def init(self):
    print("Initializing dummy frontend")

  def capture(self):
    print("Acquisition frontend capture, returning [0]")
    samplecount = self.config["samplecount"]
    return np.random.rand(samplecount).astype(np.float16)

  def arm(self):
    print("Acquisition frontend armed")
  
  def disarm(self):
    print("Acquisition frontend disarmed")

  def close(self):
    pass    
