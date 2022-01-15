#!/usr/bin/env python3

from numpy import *
import numpy as np

def VAlign(tm_in,varMgr):
  numTraces = tm_in.traceCount
  sampleCnt = tm_in.numPoints
  window_offset = varMgr.getOptionalVariable("window_offset",0)
  window_length = varMgr.getOptionalVariable("window_length",sampleCnt)
  traces = zeros((numTraces,sampleCnt),float32)
  data = zeros((numTraces,16),uint8)
  data_out = zeros((numTraces,16),uint8)
  refct = varMgr.getVariable("ref")
  savedDataIndex = 0
  reftrace = tm_in.getSingleTrace(refct)
  refmean = np.mean(reftrace[window_offset:window_length])
  print(refmean)
  input(">")
  for i in range(0,numTraces):
    if i == refct:
      traces[savedDataIndex,:] = reftrace
      data[savedDataIndex,:] = tm_in.getSingleData(i)
      data_out[savedDataIndex,:] = tm_in.getSingleDataOut(i)
      savedDataIndex += 1
    else:
      x = tm_in.getSingleTrace(i)
      x_mean = np.mean(x[window_offset:window_length])
      print("Realigning trace %d, offset %f" % (i,refmean - x_mean))
      traces[savedDataIndex,:] = x + (refmean - x_mean)
      data[savedDataIndex,:] = tm_in.getSingleData(i)
      data_out[savedDataIndex,:] = tm_in.getSingleDataOut(i)
      savedDataIndex += 1
  return (traces,data,data_out)
