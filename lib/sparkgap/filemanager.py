#!/usr/bin/env python3

# v2: hdf5

import scipy.io
import h5py
import numpy
import numpy as np
import os
import sys
# import matplotlib.pyplot as plt

class CaptureSet:
  def __init__(self,tracecount=15000,samplecount=100000,in_len=16,out_len=16,migrateData=False):
    self.writeHead = 0
    self.tracecount = tracecount
    if migrateData is False:
      self.traces = np.zeros((tracecount,samplecount),np.float32)
      self.data_in = np.zeros((tracecount,in_len),np.uint8)
      self.data_out = np.zeros((tracecount,out_len),np.uint8)
    else:
      print("CaptureSet: migrating data, not creating trace sets")

  def addTrace(self,trace,data_in,data_out):
    self.traces[self.writeHead:] = trace
    self.data_in[self.writeHead:] = data_in
    self.data_out[self.writeHead:] = data_out
    self.writeHead += 1

  def save(self,filename=None,writeHeadFix=True):
    if self.writeHead < self.tracecount - 1:
      print("CaptureSet: expecting %d traces, got %d traces, fixing" % (self.tracecount,self.writeHead + 1))
      self.traces = self.traces[0:self.writeHead]
      self.data_in = self.data_in[0:self.writeHead]
      self.data_out = self.data_out[0:self.writeHead]
    if filename is None:
      print("CaptureSet: save needs a filename (update your code)")
      return
    while os.path.exists(filename):
      print("CaptureSet: file overwrite, use a new name")
      filename = input(" > ").rstrip()
    tn = TraceManager(filename)
    tn.f.create_dataset("traces",data=self.traces)
    tn.f.create_dataset("data_in",data=self.data_in)
    tn.f.create_dataset("data_out",data=self.data_out)  

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

  def slice(self,offset,numsamples):
    print("TraceManager: vertical slicing keeping %d:%d")
    if numsamples <= 0:
      print("TraceManager: numsamples must be positive nonzero")
      return
    if (offset <= 0) or (offset + numsamples >= self.numPoints):
      print("TraceManager: offset + numsamples must be less than %d" % self.numPoints)
      return
    newtraces = np.zeros((self.numTraces,numsamples),np.float32)
    for i in range(0,len(self.traces)):
      newtraces[i] = self.traces[i][offset:offset+numsamples]
    self.traces = newtraces
    self.numPoints = numsamples
    print("TraceManager: vertical slicing complete")

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

  # should've called it this from the start fml
  @property
  def numTraces(self):
    return self.traceCount

  def getTraceCount(self):
    return self.traceCount

  def getSingleData(self,key):
    return self.data_in[key]

  def getSingleDataOut(self,key):
    return self.data_out[key]

  def getSingleTrace(self,key):
    return self.traces[key]

  def cutTraces(self,start,end):
    print("TraceManager2: Cutting traces from %d to %d" % (start,end))    
    self.tracesNew = np.zeros((self.traceCount,end - start),np.float32)
    for i in range(0,self.traceCount):
      # print(len(self.traces[i]))
      self.tracesNew[i] = self.traces[i,start:end]
    print("TraceManager2: Deleting previous trace set")
    del self.traces
    self.traces = self.tracesNew

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
  print("FileManager: Call to legacy save(). Migrate this to CaptureSet")
  sys.exit(0) 
  # tn = TraceManager(fn)
  # tn.f.create_dataset("traces",data=traces)
  # tn.f.create_dataset("data_in",data=data)
  # tn.f.create_dataset("data_out",data=data_out)

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print("This is not meant to be called directly :)")
  tm = TraceManager(sys.argv[1])
  f1 = open("inputs.txt","w")
  f2 = open("outputs.txt","w")
  for i in range(0,len(tm.data_in)):
    d1 = tm.data_in[i]
    f1.write("".join(["%02x" % x for x in d1]) + "\n")
    d2 = tm.data_out[i]
    f2.write("".join(["%02x" % x for x in d2]) + "\n")
  f1.close()
  f2.close()
