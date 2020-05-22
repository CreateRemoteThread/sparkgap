#!/usr/bin/env python3

from picoscope import ps6000
import binascii

ANALOG_OFFSET = -1.800
VRANGE_PRIMARY = 0.50
SAMPLE_RATE = 125000000
NUM_SAMPLES = 15000

class CaptureInterface():
  def __init__(self):
    print("Using PicoScope 6xxx Capture Interface")
    self.config = {}
    self.config["samplecount"] = 15000  

  def init(self):
    global SAMPLERATE, VRANGE_PRIMARY, ANALOG_OFFSET
    print("ps6000: initializing self.scope")
    self.ps = None
    self.ps = ps6000.PS6000()
    #   print("ps6000: could not initialize scope")
    #   return
    self.ps.setChannel('A','AC',VRange=0.5,enabled=True,BWLimited=False,probeAttenuation=10.0)
    # self.ps.setChannel('A','DC',VRange=5.0,enabled=True,BWLimited=False,probeAttenuation=10.0)
    self.ps.setChannel('B','DC',VRange=7.0,VOffset=0.0,enabled=True,BWLimited=False, probeAttenuation = 10.0)
    nSamples = self.config["samplecount"]
    (freq,maxSamples) = self.ps.setSamplingFrequency(SAMPLE_RATE,nSamples)
    print("ps6000: got frequency %d Hz" % freq)
    print("Executing dummy capture, please wait 1 second...")
    self.ps.setSimpleTrigger('B',1.0,'Rising',timeout_ms=1000,enabled=True)
    self.ps.runBlock()
    print("Ok, continuing in AC mode")

  def arm(self):
    self.ps.setSimpleTrigger('B',1.0,'Rising',timeout_ms=1000,enabled=True)
    self.ps.runBlock()

  def capture(self):
    self.ps.waitReady()
    return self.ps.getDataV("A",self.config["samplecount"],returnOverflow=False)

  def close(self):
    self.ps.stop()
    self.ps.close() 
