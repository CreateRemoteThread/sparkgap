#!/usr/bin/env python3

from gnuradio import gr
from gnuradio import blocks
from gnuradio import analog
import osmosdr
import time
import sys
import getopt

class top_block(gr.top_block):
  def __init__(self,num_samples=1500000,wfile="butts",sr=1800000,center_freq=65036000,bandwidth=400000):
    gr.top_block.__init__(self)
    source = osmosdr.source(args="numchan=1")
    source.set_sample_rate(sr)
    source.set_center_freq(center_freq)
    source.set_bandwidth(bandwidth,0)
    source.set_gain(20,0)
    source.set_if_gain(20.0)
    source.set_bb_gain(20,0)
    source.set_gain_mode(False,0)
    
    head = blocks.head(8,num_samples)
    sink = blocks.file_sink(4,wfile)
    float_converter = blocks.complex_to_float(1)
    # fm_demod = analog.fm_demod_cf(channel_rate=sr,audio_decim=100,deviation=75000,audio_pass=3,audio_stop=sr / 2, gain=1.0,tau=0.0)

    self.connect(source,head)
    self.connect(head,float_converter)
    self.connect((float_converter,0),(sink,0))

if __name__ == "__main__":
  CONFIG_BW = 200000
  CONFIG_FREQ = 65000000
  CONFIG_SR = 1800000
  CONFIG_SAMPLECOUNT = 18000000
  CONFIG_WFILE = "butts"
  opts,args = getopt.getopt(sys.argv[1:],"n:w:s:f:b:",["num_samples=","writefile=","sr=","freq=","bw="])
  for (opt,arg) in opts:
    if opt in ["-b","--bw"]:
      CONFIG_BW = int(arg)
    elif opt in ["-f","--freq"]:
      CONFIG_FREQ = int(arg)
    elif opt in ["-s","--sr"]:
      CONFIG_SR = int(arg)
    elif opt in ["-w","--writefile"]:
      CONFIG_WFILE = arg
    elif opt in ["-n","--num_samples"]:
      CONFIG_SAMPLECOUNT = int(arg)
  a = top_block(wfile=CONFIG_WFILE,num_samples=CONFIG_SAMPLECOUNT,sr=CONFIG_SR,bandwidth=CONFIG_BW,center_freq=CONFIG_FREQ)
  x = input(">")
  a.run()
