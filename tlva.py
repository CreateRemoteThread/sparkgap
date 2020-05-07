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

CONFIG_FILE = None

def distinguisher_fixed(data):
  return np.array_equal(data,[0xaa] * 16)

def distinguisher_even(data):
  return data[0] % 2 == 0

def distinguisher_random(data):
  return random.randint(0,10) % 2 == 0

CONFIG_DISTINGUISHER = distinguisher_fixed

def do_tlva(fn,distinguisher):
  cf = [0xAA] * 16
  df = support.filemanager.load(fn)
  tlva_fixed_traces = []
  tlva_random_traces = []
  for i in range(0,len(df['traces'])):
    if distinguisher(df['data'][i]):
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
  # print(ttrace)
  return (np.nan_to_num(ttrace[0]),np.nan_to_num(ttrace[1]))

CONFIG_WRITEFILE = None

if __name__ == "__main__":
  optlist, args = getopt.getopt(sys.argv[1:],"f:d:w:",["distinguisher=","writefile="])
  for arg, value in optlist:
    if arg == "-f":
      CONFIG_FILE = value
    elif arg in ("-d","--distinguisher"):
      if value.upper() == "EVEN":
        print("* Using EVEN distinguisher (is the first byte of plaintext even)")
        CONFIG_DISTINGUISHER = distinguisher_even
      elif value.upper() == "FIXED":
        print("* Using FIXED distinguisher (is the plaintext 0xAA * 16)")
        CONFIG_DISTINGUISHER = distinguisher_fixed
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
  (tt,tp) = do_tlva(CONFIG_FILE,CONFIG_DISTINGUISHER)
  fig,ax1 = plt.subplots()
  fig.canvas.set_window_title("Test Vector Leakage Assessment")
  ax1.set_title("T-Value")
  ax1.set_xlabel("Sample")
  ax1.set_ylabel("T-Test Value")
  ax1.plot(tt)
  if CONFIG_WRITEFILE is not None:
    plt.savefig(CONFIG_WRITEFILE)
  else:
    plt.show()
