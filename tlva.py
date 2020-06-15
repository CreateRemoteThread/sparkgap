#!/usr/bin/env python3

#  TVLA leakfinder
# -----------------
#  -f <traceset>
#  -d <distinguisher>
#     - even
#     - fixed
#     - random
#     - (an attack name), same as dpa
#  -b <bytenum:default 0>
#  -k <keyguess:default 0>>

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

def distinguisher_fixed(data,roundmkeyguess):
  return np.array_equal(data,[0xaa] * 16)

def distinguisher_even(data,round,keyguess):
  # print("%02x" % data[round])
  return data[round] % 2 == 0

# keeloq is 66 bits...
def unpackKeeloq(plaintext):
  out = ""
  for i in range(0,9):
    out = format(plaintext[i],"08b") + out
  return out[6:]

def distinguisher_keeloq(data,round):
  f = unpackKeeloq(data)
  # print(f)
  fc = f[0:32]
  return fc[round] == '1'

def distinguisher_random(data,round,keyguess):
  return random.randint(0,10) % 2 == 0

CONFIG_DISTINGUISHER = distinguisher_fixed

# plaintext dpa "t-test"
def do_dpatest(fn,leakmodel,round,CONFIG_BYTE,CONFIG_KEYGUESS):
  print("DPA Test rework WIP, come back later...")
  sys.exit(0)

def do_tlva(fn,leakmodel,round,CONFIG_BYTE,CONFIG_KEYGUESS):
  cf = [0xAA] * 16
  tlva_fixed_traces = []
  tlva_random_traces = []
  for tracenum in range(0,fn.traceCount):
    if leakmodel.distinguisher(tracenum,CONFIG_BYTE,CONFIG_KEYGUESS):
      tlva_fixed_traces.append(fn.getSingleTrace(tracenum))
    else:
      tlva_random_traces.append(fn.getSingleTrace(tracenum))
  print("Fixed traces count: %d" % len(tlva_fixed_traces))
  print("Random traces count: %d" % len(tlva_random_traces))
  if len(tlva_fixed_traces) == 0:
    print("Padding fixed traces...")
    tlva_fixed_traces = np.array([[np.nan for _ in range(fn.numPoints)]])
  with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    ttrace = scipy.stats.ttest_ind(tlva_random_traces,tlva_fixed_traces,axis=0,equal_var=False)
  return (np.nan_to_num(ttrace[0]),np.nan_to_num(ttrace[1]),fn.numPoints)

CONFIG_WRITEFILE = None

DO_TLVA  = 0
DO_DPA   = 1
CONFIG_STRATEGY = DO_TLVA

leakmodel = None

class SpecialLeakModel:
  def __init__(self):
    self.customDistinguisher = None
    pass

  def loadPlaintextArray(self,pts):
    self.plaintexts = pts

  def loadCiphertextArray(self,cts):
    self.ciphertexts = cts

  def distinguisher(self,xindex,byte,key):
    return self.customDistinguisher(self.plaintexts[xindex],byte,key)

if __name__ == "__main__":
  optlist, args = getopt.getopt(sys.argv[1:],"f:d:w:r:b:k:",["byte=","key=","distinguisher=","writefile=","round=","dpa"])
  CONFIG_ROUND = 0
  CONFIG_BYTE = 0
  CONFIG_KEY = 0
  for arg, value in optlist:
    if arg == "-f":
      CONFIG_FILE = value
    elif arg in ["--byte","-b"]:
      CONFIG_BYTE = int(value,0)
    elif arg in ["--key","-k"]:
      CONFIG_KEY = int(value,0)
    elif arg in ["--dpa"]:
      print("* Using raw plaintext DPA technique")
      CONFIG_STRATEGY = DO_DPA
    elif arg in ["-r","--round"]:
      CONFIG_ROUND = int(value)
    elif arg in ["-d","--distinguisher"]:
      if value.upper() == "EVEN":
        leakmodel = SpecialLeakModel()
        leakmodel.customDistinguisher =distinguisher_even
      elif value.upper() == "FIXED":
        leakmodel = SpecialLeakModel()
        leakmodel.customDistinguisher =distinguisher_fixed
      elif value.upper() == "RANDOM":
        leakmodel = SpecialLeakModel()
        leakmodel.customDistinguisher =distinguisher_random
      else:
        leakmodel = support.attack.fetchModel(value)
    elif arg in ["-w","--writefile"]:
      CONFIG_WRITEFILE = value
  if CONFIG_WRITEFILE is not None:
    mpl.use("Agg")  
  import matplotlib.pyplot as plt
  if CONFIG_FILE is None:
    print("You must specify a file")
    sys.exit(0)
  fn = support.filemanager.TraceManager(CONFIG_FILE)
  leakmodel.loadPlaintextArray(fn.loadPlaintexts())
  if CONFIG_STRATEGY == DO_TLVA:
    (tt,tp,numSamples) = do_tlva(fn,leakmodel,CONFIG_ROUND,CONFIG_BYTE,CONFIG_KEY)
  elif CONFIG_STRATEGY == DO_DPA:
    (tt,tp,numSamples) = do_dpatest(fn,leakmodel,CONFIG_ROUND,0,0)
  else:
    print("Unknown value of CONFIG_STRATEGY, %d" % CONFIG_STRATEGY)
    sys.exit(0)
  fig,ax1 = plt.subplots()
  fig.canvas.mpl_connect("button_press_event",onclick)
  fig.canvas.set_window_title("Test Vector Leakage Assessment")
  ax1.set_title("T-Value")
  ax1.set_xlabel("Sample")
  ax1.set_ylabel("T-Test Value")
  ax1.plot(tt)
  tlen = numSamples
  if CONFIG_STRATEGY == DO_TLVA:
    print("Drawing 4.5 markers")
    ax1.hlines(y=4.5,xmin=0,xmax=tlen,color='r')
    ax1.hlines(y=-4.5,xmin=0,xmax=tlen,color='r')
  if CONFIG_WRITEFILE is not None:
    plt.savefig(CONFIG_WRITEFILE)
  else:
    plt.show()
