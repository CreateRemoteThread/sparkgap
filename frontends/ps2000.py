#!/usr/bin/env python3

from picoscope import ps2000a
import binascii

plt = None

# self.config["pico_offset"] = -2.39
# self.config["pico_vrange"] = 0.2
# self.config["samplerate"] = 125000000
# self.config["pico_atten"] = 10.0

# TEST

class CaptureInterface():
  def __init__(self):
    print("Using PicoScope 2xxx Capture Interface")
    self.config = {}
    self.config["samplecount"] = 15000
    self.config["pico_timeout"] = 2000
    self.config["pico_offset"] = -2.39
    self.config["pico_vrange"] = 0.2
    self.config["pico_atten"] = 10.0
    self.config["samplerate"] = 125000000
    self.config["DEBUG"] = False
    print("== REMEMBER TO SET samplerate, pico_voffset, pico_vrange == ")
    print("== REMEMBER TO SET DEBUG to True to graph results per-run == ")

  def init(self):
    print("ps2000: initializing self.scope")
    if self.config["DEBUG"]:
      print("importing as plt")
      global plt
      import matplotlib.pyplot as pltx
      plt = pltx
    self.ps = None
    self.ps = ps2000a.PS2000a()
    self.ps.setChannel('A','DC',VRange=self.config["pico_vrange"],VOffset=self.config["pico_offset"],enabled=True,BWLimited=False,probeAttenuation=self.config["pico_atten"])
    self.ps.setChannel('B','DC',VRange=10.0,VOffset=0.0,enabled=True,BWLimited=False,probeAttenuation=self.config["pico_atten"])
    nSamples = self.config["samplecount"]
    (freq,maxSamples) = self.ps.setSamplingFrequency(self.config["samplerate"],nSamples)
    print("ps2000: got frequency %d Hz, %d max samples" % (freq,maxSamples))
    self.freq = freq
    self.maxSamples = maxSamples

  def arm(self):
    self.ps.setSimpleTrigger('B',1.0,'Rising',timeout_ms=self.config["pico_timeout"],enabled=True)
    self.ps.runBlock(pretrig = 0.01)

  def capture(self):
    global plt
    self.ps.waitReady()
    # print(self.maxSamples // 2)
    data = self.ps.getDataV("A",self.config["samplecount"],returnOverflow=False)
    if self.config["DEBUG"]:
      data2 = self.ps.getDataV("B",self.config["samplecount"],returnOverflow=False)
      fig,ax1 = plt.subplots()
      ax1.plot(data2)
      ax2 = ax1.twinx()
      # plt.plot(data)
      ax2.plot(data)
      plt.show()
    return data

  def close(self):
    self.ps.stop()
    self.ps.close() 
