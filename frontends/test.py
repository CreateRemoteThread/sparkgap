#!/usr/bin/env python3

import sys

class CaptureInterface():
  def __init__(self):
    self.config = {}
    self.config["samplecount"] = 5000
    print("Acquisition frontend ready")

  def init(self):
    print("Initializing dummy frontend")

  def capture(self):
    print("Acquisition frontend capture, returning [0]")
    return [0]

  def arm(self):
    print("Acquisition frontend armed")
  
  def disarm(self):
    print("Acquisition frontend disarmed")

  def close(self):
    pass    
