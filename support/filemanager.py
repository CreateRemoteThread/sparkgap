#!/usr/bin/env python3

# v2: hdf5

import scipy.io
import h5py
import numpy
import os
import sys
# import matplotlib.pyplot as plt

class TraceSet:
  def __init__(self,key):
    print("TraceSet: Initialized blank TraceSet with key %s" % key)
    self.key = key
    self.traces_fn = None
    self.traces = None
    self.data_fn = None
    self.data = None
    self.data_out_fn = None
    self.data_out = None

class TraceManager:
  def cleanup(self):
    print("TraceManager: saveBlock wrapping up")
    if self.f is not None:
      self.f.close()

  # this needed to use weights in the old trace format, this is
  def getMeant(self):
    print("TraceManager2: getMeant called")
    m = numpy.mean(self.traces,axis=0)    
    # plt.plot(m)
    # plt.show()
    return m

  def loadCiphertexts(self):
    print("TraceManager2: loadCiphertexts called")
    return self.f["data_out"]
    pass

  def loadPlaintexts(self):
    print("TraceManager2: loadPlaintexts called")
    return self.f["data_in"]
    # pass

  def getTraceCount(self):
    return self.traceCount

  def getSingleData(self,key):
    return self.data_in[key]

  def getSingleDataOut(self,key):
    return self.data_out[key]

  def getSingleTrace(self,key):
    return self.traces[key]

  def __init__(self,filename):
    print("TraceManager2: Initializing with filename %s" % filename)
    self.fn = filename
    self.numPoints = None
    self.traceCount = None
    if os.path.isfile(filename) is False:
      print("TraceManager2: %s is not a file, creating a new one" % filename)
      self.f = h5py.File(filename,"w")
      return
    else:
      self.f = h5py.File(filename,"a")
      self.traces = self.f["traces"]
      self.data_in = self.f["data_in"]
      self.data_out = self.f["data_out"]
    traceCount = len(self.traces)
    numPoints = len(self.traces[0])
    print("TraceManager2: %d traces with %d points each loaded." % (traceCount,numPoints))
    self.traceCount = traceCount
    self.numPoints = numPoints

def save(fn,traces=None,data=None,data_out=None,freq=0,additionalParams={}):
  tn = TraceManager(fn)
  tn.f.create_dataset("traces",data=traces)
  tn.f.create_dataset("data_in",data=data)
  tn.f.create_dataset("data_out",data=data_out)

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print("This is not meant to be called directly :)")
