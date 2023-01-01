#!/usr/bin/env python3

from picoscope import ps2000a
import binascii
import time

plt = None

# self.config["pico_offset"] = 0
# self.config["pico_vrange"] = 0.5
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
    self.config["pico_coupling"] = "DC"
    self.config["samplerate"] = 125000000
    self.config["DEBUG"] = False
    print("== REMEMBER TO SET samplerate, pico_offset, pico_vrange == ")
    print("== REMEMBER TO SET DEBUG to True to graph results per-run == ")

  def init(self):
    print("ps2000: initializing self.scope")
    if self.config["DEBUG"]:
      print("importing as plt")
      global plt
      import matplotlib.pyplot as pltx
      plt = pltx
    self.samplestart = None
    self.samplecount = None
    self.capturecount = None
    self.ps = None
    self.ps = ps2000a.PS2000a()
    self.ps.setChannel('A',self.config["pico_coupling"],VRange=self.config["pico_vrange"],VOffset=self.config["pico_offset"],enabled=True,BWLimited=False,probeAttenuation=self.config["pico_atten"])
    self.ps.setChannel('B','DC',VRange=10.0,VOffset=0.0,enabled=True,BWLimited=False,probeAttenuation=self.config["pico_atten"])
    if "capturecount" in self.config.keys():
      print("ps2000: overriding samplecount with capturecount")
      print("ps2000: will CAPTURE capturecount, will SAVE samplecount")  
      nSamples = self.config["capturecount"]
      self.samplestart = self.config["samplestart"]
      self.samplecount = self.config["samplecount"]
      self.capturecount = nSamples
    else:
      nSamples = self.config["samplecount"]
      self.capturecount=nSamples
    (freq,maxSamples) = self.ps.setSamplingFrequency(self.config["samplerate"],nSamples)
    if self.config["pico_coupling"] == "AC":
      print("Firing block to flush DC offset...")
      self.ps.runBlock()
      time.sleep(3.0)
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
    data = self.ps.getDataV("A",self.capturecount,returnOverflow=False)
    if self.config["DEBUG"]:
      data2 = self.ps.getDataV("B",self.capturecount,returnOverflow=False)
      fig,ax1 = plt.subplots()
      ax1.plot(data,color="red")
      ax1.set_ylabel("data - red")
      ax2 = ax1.twinx()
      ax2.set_ylabel("trigger - blue")
      if self.samplecount != None and self.samplestart != None:
        ax2.plot(data2[self.samplestart:self.samplestart + self.samplecount])
      else:      
        ax2.plot(data2)
      plt.show()
    if self.samplecount != None and self.samplestart != None:
      print(self.samplestart)
      print(self.samplecount)
      print(len(data))
      return data[self.samplestart:self.samplestart + self.samplecount]
    else:
      return data

  def close(self):
    self.ps.stop()
    self.ps.close() 
