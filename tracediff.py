#!/usr/bin/env python3

import time
import scipy
import scipy.stats
import numpy as np
import sys
import matplotlib as mpl
import matplotlib.pyplot as plt
import sparkgap.filemanager
import getopt
import copy
import os
from numpy import *

def doCompareTraces_SINGLE(tn1):
  tm_in1 = sparkgap.filemanager.TraceManager(tn1)
  tlva_group1_traces = []
  tlva_group2_traces = []
  group1_avg = None
  group1_avg_cnt = 0
  group2_avg = None
  group2_avg_cnt = 0
  for f in range(0,tm_in1.getTraceCount()):
    if tm_in1.getSingleData(f)[0] == 0xF0:
      tlva_group1_traces.append(tm_in1.getSingleTrace(f))
      if group1_avg is None:
        group1_avg = tm_in1.getSingleTrace(f) * 1.0
        print(group1_avg)
        group1_avg_cnt += 1
      else:
        group1_avg += tm_in1.getSingleTrace(f) * 1.0
        group1_avg_cnt += 1
    else:
      tlva_group2_traces.append(tm_in1.getSingleTrace(f))
      if group2_avg is None:
        group2_avg = tm_in1.getSingleTrace(f) * 1.0
        group2_avg_cnt += 1
      else:
        group2_avg += tm_in1.getSingleTrace(f) * 1.0
        group2_avg_cnt += 1
  group1_avg /= group1_avg_cnt
  group2_avg /= group2_avg_cnt
  fig,(ax1,ax2) = plt.subplots(2,1)
  ax1.set_title("Difference of Means")
  ax1.plot(abs(group1_avg - group2_avg))
  ax2.set_title("Avg Std (Noise)")
  ax2.plot(np.std(tlva_group1_traces,axis=0,keepdims=True)[0])
  ax2.plot(np.std(tlva_group2_traces,axis=0,keepdims=True)[0])
  plt.show()
  return
  ttrace = scipy.stats.ttest_ind(tlva_group1_traces, tlva_group2_traces,axis=0,equal_var=False)
  (tt,tn,_) =  (np.nan_to_num(ttrace[0]),np.nan_to_num(ttrace[1]),tm_in1.numPoints)
  print("POO")

TRACE_FILES = []
CONFIG_OFFSET = None
CONFIG_SAMPLES = None

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

lastTime = 0.0
lastX = 0

def onclick(event):
  global lastTime, lastX, CONFIG_OFFSET
  OFFSET = CONFIG_OFFSET
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
      lastX += OFFSET
      print("MARK: %d" % lastX)
    else:
      localX = int(event.xdata)
      fromX = min(lastX,localX)
      toX = max(lastX,localX)
      dist = toX - fromX
      fromX += OFFSET
      toX += OFFSET
      print("FROM %d TO %d DIST %d" % (fromX,toX,dist))
      lastX = localX

def doCompareTraces(tn1,tn2):
  global CONFIG_OFFSET,CONFIG_SAMPLES
  tm_in1 = sparkgap.filemanager.TraceManager(tn1)
  trace_avg1 = tm_in1.getMeant()
  tm_in2 = sparkgap.filemanager.TraceManager(tn2)
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
  fig.canvas.mpl_connect("button_press_event",onclick)
  a1.set_title("Averaged Traces")
  a1.plot(trace_avg1, label=os.path.basename(tn1))
  a1.plot(trace_avg2, label=os.path.basename(tn2))
  a1.legend()
  a2.set_title("Difference of Means")
  a2.plot(abs(trace_avg1 - trace_avg2))
  a3.set_title("Avg Standard Deviation (Noise)")
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
    doCompareTraces_SINGLE(TRACE_FILES[0])
  elif len(TRACE_FILES) == 2:
    doCompareTraces(TRACE_FILES[0],TRACE_FILES[1])
  else:
    print("You must specify exactly 1 or 2 trace files with -f")
    sys.exit(0)

