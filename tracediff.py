#!/usr/bin/env python3

import scipy
import scipy.stats
import numpy as np
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

import random
# group 1 is random, group2  is fixed.
def doTLVA(tm_in1,tm_in2):
  global CONFIG_OFFSET,CONFIG_SAMPLES
  if CONFIG_OFFSET is None or CONFIG_SAMPLES is None:
    print("Error: CONFIG_OFFSET or CONFIG_SAMPLES is None when doTLVA is called")
    sys.exit(0)
  print("Loading traces for TLVA")
  tlva_group1_traces = []
  tlva_group2_traces = []
  for f in range(0,tm_in1.getTraceCount()):
    if random.randint(0,6) % 2 == 0:
      tlva_group1_traces.append(tm_in1.getSingleTrace(f)[CONFIG_OFFSET:CONFIG_OFFSET+CONFIG_SAMPLES])
  for f in range(0,tm_in2.getTraceCount()):
    if random.randint(0,6) % 2 == 0:
      tlva_group2_traces.append(tm_in2.getSingleTrace(f)[CONFIG_OFFSET:CONFIG_OFFSET+CONFIG_SAMPLES])
    else:
      tlva_group1_traces.append(tm_in2.getSingleTrace(f)[CONFIG_OFFSET:CONFIG_OFFSET+CONFIG_SAMPLES])
  ttrace = scipy.stats.ttest_ind(tlva_group1_traces, tlva_group2_traces,axis=0,equal_var=False)
  return (np.nan_to_num(ttrace[0]),np.nan_to_num(ttrace[1]),tm_in1.numPoints)

def doCompareTraces(tn1,tn2):
  global CONFIG_OFFSET,CONFIG_SAMPLES
  tm_in1 = support.filemanager.TraceManager(tn1)
  trace_avg1 = tm_in1.getMeant()
  tm_in2 = support.filemanager.TraceManager(tn2)
  trace_avg2 = tm_in2.getMeant()
  if len(trace_avg1) != len(trace_avg2):
    print("The traces do not have equal lengths, I can't use this")
  if CONFIG_OFFSET is None:
    CONFIG_OFFSET = 0
  if CONFIG_SAMPLES is None:
    CONFIG_SAMPLES = len(trace_avg1) - 1 - CONFIG_OFFSET
  trace_avg1 = trace_avg1[CONFIG_OFFSET:CONFIG_OFFSET + CONFIG_SAMPLES]
  trace_avg2 = trace_avg2[CONFIG_OFFSET:CONFIG_OFFSET + CONFIG_SAMPLES]
  fig,(a1,a2,a3) = plt.subplots(3,1)
  a1.set_title("Averaged Traces")
  a1.plot(trace_avg1)
  a1.plot(trace_avg2)
  a2.set_title("Difference of Means")
  a2.plot(abs(trace_avg1 - trace_avg2))
  a3.set_title("Standard Deviation")
  # (nn0,nn1,points) = doTLVA(tm_in1,tm_in2)
  group1_traces = []
  for f in range(0,tm_in1.getTraceCount()):
    group1_traces.append(tm_in1.getSingleTrace(f)[CONFIG_OFFSET:CONFIG_OFFSET+CONFIG_SAMPLES])
  a3.plot(np.std(group1_traces,axis=0,keepdims=True)[0])
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

