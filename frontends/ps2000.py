#!/usr/bin/env python3

from picoscope import ps2000a
import binascii

ANALOG_OFFSET = 0.00
VRANGE_PRIMARY = 0.10
SAMPLE_RATE = 40000000
NUM_SAMPLES = 15000

# TEST

class CaptureInterface():
  def __init__(self):
    print("Using PicoScope 2xxx Capture Interface")
    self.config = {}
    self.config["samplecount"] = 15000

  def init(self):
    global SAMPLERATE, VRANGE_PRIMARY, ANALOG_OFFSET
    print("ps2000: initializing self.scope")
    self.ps = None
    self.ps = ps2000a.PS2000a()
    #   print("ps2000: could not initialize scope")
    #   return
    self.ps.setChannel('A','DC',VRange=VRANGE_PRIMARY,VOffset=ANALOG_OFFSET,enabled=True,BWLimited=False)
    self.ps.setChannel('B','DC',VRange=7.0,VOffset=0.0,enabled=True,BWLimited=False)
    nSamples = self.config["samplecount"]
    (freq,maxSamples) = self.ps.setSamplingFrequency(SAMPLE_RATE,nSamples)
    print("ps2000: got frequency %d Hz" % freq)

  def arm(self):
    self.ps.setSimpleTrigger('B',1.0,'Rising',timeout_ms=100,enabled=True)
    self.ps.runBlock()

  def capture(self):
    self.ps.waitReady()
    return self.ps.getDataV("A",self.config["samplecount"],returnOverflow=False)

  def close(self):
    self.ps.stop()
    self.ps.close() 
