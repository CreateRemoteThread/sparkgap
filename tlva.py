#!/usr/bin/env python3

import scipy
import scipy.stats
import getopt
import random
import sys
import numpy as np
import warnings
import matplotlib as mpl
import support.filemanager
import support.attack
import time

CONFIG_FILE = None

lastTime = 0.0
lastX = 0

def onclick(event):
  global lastTime, lastX
  t = time.time()
  if t - lastTime < 0.200:
    print("debounce - nope")
    return
  elif event.xdata is None:
    print("skip - event.xdata (click on graph) is none")
    return
  else:
    lastTime = t
    if lastX == 0:
      lastX = int(event.xdata)
      print("MARK: %d" % lastX)
    else:
      localX = int(event.xdata)
      fromX = min(lastX,localX)
      toX = max(lastX,localX)
      dist = toX - fromX
      print("FROM %d TO %d DIST %d" % (fromX,toX,dist))
      lastX = localX

def distinguisher_fixed(data,round):
  return np.array_equal(data,[0xaa] * 16)

def distinguisher_even(data,round):
  return data[round] % 2 == 0

def unpackKeeloq(plaintext):
  out = ""
  for i in range(0,9):
    out = format(plaintext[i],"08b") + out
  print(out[6:])
  return out[6:]

def distinguisher_keeloq(data,round):
  f = unpackKeeloq(data)
  return f[round] == '1'

def distinguisher_random(data,round):
  return random.randint(0,10) % 2 == 0

CONFIG_DISTINGUISHER = distinguisher_fixed

def do_tlva(fn,distinguisher,round):
  cf = [0xAA] * 16
  df = support.filemanager.load(fn)
  tlva_fixed_traces = []
  tlva_random_traces = []
  for i in range(0,len(df['traces'])):
    if distinguisher(df['data'][i],round):
      tlva_fixed_traces.append(df['traces'][i])
    else:
      tlva_random_traces.append(df['traces'][i])
  print("Fixed traces count: %d" % len(tlva_fixed_traces))
  print("Random traces count: %d" % len(tlva_random_traces))
  if len(tlva_fixed_traces) == 0:
    print("Padding fixed traces...")
    tlva_fixed_traces = np.array([[np.nan for _ in range(len(df['traces'][0]))]])
  with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    ttrace = scipy.stats.ttest_ind(tlva_random_traces,tlva_fixed_traces,axis=0,equal_var=False)
  return (np.nan_to_num(ttrace[0]),np.nan_to_num(ttrace[1]),len(df['traces'][0]))

CONFIG_WRITEFILE = None

if __name__ == "__main__":
  optlist, args = getopt.getopt(sys.argv[1:],"f:d:w:r:",["distinguisher=","writefile=","round="])
  CONFIG_ROUND = 0
  for arg, value in optlist:
    if arg == "-f":
      CONFIG_FILE = value
    elif arg in ("-r","--round"):
      CONFIG_ROUND = int(value)
    elif arg in ("-d","--distinguisher"):
      if value.upper() == "EVEN":
        print("* Using EVEN distinguisher (is the first byte of plaintext even)")
        CONFIG_DISTINGUISHER = distinguisher_even
      elif value.upper() == "FIXED":
        print("* Using FIXED distinguisher (is the plaintext 0xAA * 16)")
        CONFIG_DISTINGUISHER = distinguisher_fixed
      elif value.upper() == "KEELOQ":
        print("* Using KEELOQ SPECIAL distinguisher")
        CONFIG_DISTINGUISHER = distinguisher_keeloq
      elif value.upper() == "RANDOM":
        print("* Using RANDOM distinguisher. Traces into random buckets, testing for null hypothesis")
        CONFIG_DISTINGUISHER = distinguisher_random
      else:
        print("Unknown distinguisher. Valid values are EVEN, FIXED, RANDOM")
        sys.exit(0)
    elif arg in ("-w","--writefile"):
      CONFIG_WRITEFILE = value
  if CONFIG_WRITEFILE is not None:
    mpl.use("Agg")  
  import matplotlib.pyplot as plt
  (tt,tp,numSamples) = do_tlva(CONFIG_FILE,CONFIG_DISTINGUISHER,CONFIG_ROUND)
  fig,ax1 = plt.subplots()
  fig.canvas.mpl_connect("button_press_event",onclick)
  fig.canvas.set_window_title("Test Vector Leakage Assessment")
  ax1.set_title("T-Value")
  ax1.set_xlabel("Sample")
  ax1.set_ylabel("T-Test Value")
  ax1.plot(tt)
  tlen = numSamples
  ax1.hlines(y=4.5,xmin=0,xmax=tlen,color='r')
  ax1.hlines(y=-4.5,xmin=0,xmax=tlen,color='r')
  if CONFIG_WRITEFILE is not None:
    plt.savefig(CONFIG_WRITEFILE)
  else:
    plt.show()
