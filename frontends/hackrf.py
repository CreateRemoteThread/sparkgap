#!/usr/bin/env python3

# hackrf frontend.

import sys
import subprocess
import numpy

class CaptureInterface():
  def __init__(self):
    self.config = {}
    self.config["samplecount"] = 5000
    self.config["freq"] = 16e6
    self.config["bw"] = 1e6
    print("HackRF ext.trig. frontend ready")

  def init(self):
    print("hackrf frontend init()")
    self.hackrf_proc = None

  def capture(self):
    print("hackrf acquire")
    try:
      stdout,stderr = self.hackrf_proc.communicate(timeout=5.0)
    except subprocess.TimeoutExpired as e:
      print("Error: subprocess timed out")
      return [0]
    self.hackrf_proc = None
    if b"exit" not in stderr:
      print("Error: no exit detected")
      return [0]
    # print(stdout)
    # print(stderr)
    return numpy.fromstring(stdout, dtype=numpy.uint8)

  # hackrf_transfer -H -d <serial number> -a 0 -l 32 -g 32 -r rx1.cs8
  def arm(self):
    try:
      self.hackrf_proc = subprocess.Popen(["hackrf_transfer","-H","-f","8100000","-s","4000000","-a","0","-l","32","-g","32","-n","10000","-r","-"],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=False)
    except:
      print("hackrf: could not open process")
      sys.exit(0)
    print("hackrf: started process")
  
  def disarm(self):
    print("Acquisition frontend disarmed")
    print(self.hackrf_proc)

  def close(self):
    pass    
