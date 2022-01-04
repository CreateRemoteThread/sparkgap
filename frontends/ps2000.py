#!/usr/bin/env python3

DEBUG = True

from picoscope import ps2000a
if DEBUG:
  import matplotlib.pyplot as plt
import binascii

ANALOG_OFFSET = -2.39
VRANGE_PRIMARY = 0.2
# SAMPLE_RATE = 125000000
SAMPLE_RATE = 125000000
PROBE_ATTEN = 10.0

# TEST

class CaptureInterface():
  def __init__(self):
    print("Using PicoScope 2xxx Capture Interface")
    self.config = {}
    self.config["samplecount"] = 15000
    self.config["pico_timeout"] = 2000

  def init(self):
    global SAMPLERATE, VRANGE_PRIMARY, ANALOG_OFFSET
    print("ps2000: initializing self.scope")
    self.ps = None
    self.ps = ps2000a.PS2000a()
    self.ps.setChannel('A','DC',VRange=VRANGE_PRIMARY,VOffset=ANALOG_OFFSET,enabled=True,BWLimited=False,probeAttenuation=PROBE_ATTEN)
    self.ps.setChannel('B','DC',VRange=10.0,VOffset=0.0,enabled=True,BWLimited=False,probeAttenuation=PROBE_ATTEN)
    nSamples = self.config["samplecount"]
    (freq,maxSamples) = self.ps.setSamplingFrequency(SAMPLE_RATE,nSamples)
    print("ps2000: got frequency %d Hz, %d max samples" % (freq,maxSamples))
    self.freq = freq
    self.maxSamples = maxSamples

  def arm(self):
    self.ps.setSimpleTrigger('B',1.0,'Rising',timeout_ms=self.config["pico_timeout"],enabled=True)
    self.ps.runBlock(pretrig = 0.01)

  def capture(self):
    self.ps.waitReady()
    print(self.maxSamples // 2)
    data = self.ps.getDataV("A",self.config["samplecount"],returnOverflow=False)
    if DEBUG:
      data2 = self.ps.getDataV("B",self.config["samplecount"],returnOverflow=False)
      plt.plot(data)
      plt.plot(data2)
      plt.show()
    return data

  def close(self):
    self.ps.stop()
    self.ps.close() 
