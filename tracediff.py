#!/usr/bin/env python3

import sys
import matplotlib as mpl
import matplotlib.pyplot as plt
import support.filemanager
import getopt
from numpy import *

def doSinglePlot(tracename):
  tm_in = support.filemanager.TraceManager(tracename)
  plt.plot(tm_in.getMeant())
  plt.show()
  sys.exit(0)

TRACE_FILES = []
CONFIG_OFFSET = None
CONFIG_SAMPLES = None

def doSingleTrace(tracename):
  global CONFIG_OFFSET,CONFIG_SAMPLES
  tm_in = support.filemanager.TraceManager(tracename)
  trace_avg = tm_in.getMeant()
  f,ax = plt.subplots(1,1)
  ax.set_title("Averaged Traces")
  ax.plot(trace_avg)
  plt.show()

def doCompareTraces(tn1,tn2):
  tm_in = support.filemanager.TraceManager(tn1)
  trace_avg1 = tm_in.getMeant()
  tm_in = support.filemanager.TraceManager(tn2)
  trace_avg2 = tm_in.getMeant()
  if len(trace_avg1) != len(trace_avg2):
    print("The traces do not have equal lengths, I can't use this")
  fig,(a1,a2) = plt.subplots(2,1)
  a1.set_title("Averaged Traces")
  a1.plot(trace_avg1)
  a1.plot(trace_avg2)
  2.set_title("Difference of Means")
  a2.plot(abs(trace_avg1 - trace_avg2))
  plt.show()
  
if __name__ == "__main__":
  opts,remainder = getopt.getopt(sys.argv[1:],"f:o:n:",["file=","offset=","samples="])
  for opt, arg in opts:
    if opt in ("-f","--file"):
      TRACE_FILES.append(arg)
    elif opt in ("-o","--offset"):
      CONFIG_OFFSET = int(arg)
    elif opt in ("-n","--samples"):
      CONFIG_SAMPLES = int(arg)
  if len(TRACE_FILES) == 1:
    doSingleTrace(TRACE_FILES[0])
  elif len(TRACE_FILES) == 2:
    doCompareTraces(TRACE_FILES[0],TRACE_FILES[1])
  else:
    print("You must specify exactly 1 or 2 trace files with -f")
    sys.exit(0)

