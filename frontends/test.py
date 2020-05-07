#!/usr/bin/env python3

import sys

class CaptureInterface():
  def __init__(self):
    self.config = {}
    self.config["samplecount"] = 5000
    print("Acquisition frontend ready")

  def arm(self):
    print("Acquisition frontend armed")
  
  def disarm(self):
    print("Acquisition frontend disarmed")

  def close(self):
    pass    
