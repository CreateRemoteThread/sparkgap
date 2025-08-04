#!/usr/bin/env python3

import sparkgap.slipnslide
from numpy import *
import numpy as np

def doSlicer(tm_in,varMgr):
  CONFIG_REFTRACE = varMgr.getVariable("ref")
  CONFIG_REF_OFFSET = varMgr.getVariable("ref_offset")
  CONFIG_REF_LENGTH = varMgr.getVariable("ref_length")
  CONFIG_SLICE_DIST = varMgr.getVariable("slicedist")
  CONFIG_WRITEFILE = varMgr.getVariable("writefile")
  CONFIG_SAD_CUTOFF = varMgr.getVariable("sad_cutoff")
  maxSlicesBackwards = varMgr.getVariable("slices_backwards")
  maxSlicesForwards = varMgr.getVariable("slices_forwards")
  newSampleCount = (maxSlicesBackwards + maxSlicesForwards) * (3 + CONFIG_REF_LENGTH)
  numTraces = tm_in.traceCount
  traces = zeros((numTraces,newSampleCount),tm_in.getDtype())
  data = zeros((numTraces,16),uint8)
  data_out = zeros((numTraces,16),uint8)
  numTraces = tm_in.traceCount
  se = sparkgap.slipnslide.SliceEngine(tm_in)
  for i in range(0,numTraces):
    print("Slicing trace %d" % i)
    traces[i:] = se.FindSlices(i, CONFIG_REF_OFFSET, CONFIG_REF_LENGTH,CONFIG_SLICE_DIST,CONFIG_SAD_CUTOFF,maxSlicesBackwards,maxSlicesForwards)
    data[i,:] = tm_in.getSingleData(i)
    data_out[i,:] = tm_in.getSingleDataOut(i)
  print("Returning data, don't forget to commit!")
  return (traces,data,data_out)
  # sparkgap.filemanager.save(CONFIG_WRITEFILE,traces=traces,data=data,data_out=data_out)

