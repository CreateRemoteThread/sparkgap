#!/usr/bin/env python3

# hackrf frontend.

import sys
import subprocess
import numpy

class CaptureInterface():
  def __init__(self):
    self.config = {}
    print("HackRF ext.trig. frontend ready")

  def init(self):
    print("hackrf frontend init()")
    if "samplecount" not in self.config.keys():
      self.config["samplecount"] = 50000
    if "frequency" not in self.config.keys():
      self.config["frequency"] = 8000000
    if "samplerate" not in self.config.keys():
      self.config["samplerate"] = 2000000
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
    ns = numpy.fromstring(stdout, dtype=numpy.int8)
    paired = ns.reshape(-1,2)
    return paired[:,0] + 1j * paired[:,1]

  # hackrf_transfer -H -d <serial number> -a 0 -l 32 -g 32 -r rx1.cs8
  def arm(self):
    print(self.config)
    try:
      self.hackrf_proc = subprocess.Popen(["hackrf_transfer","-H","-f","%d" % self.config["frequency"],"-s","%d" % self.config["samplerate"],"-a","1","-l","32","-g","32","-n","%d" % self.config["samplecount"],"-r","-"],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=False)
    except Exception as e:
      print(self.config["frequency"])
      print("hackrf: could not open process")
      print(e)
      sys.exit(0)
    print("hackrf: started process")
  
  def disarm(self):
    print("Acquisition frontend disarmed")
    print(self.hackrf_proc)

  def close(self):
    pass    
