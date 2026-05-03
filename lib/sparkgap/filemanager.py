#!/usr/bin/env python3

import scipy.io
import h5py
import numpy
import numpy as np
import os
import sys
import random

class CaptureSet:
  def __init__(self,tracecount=15000,samplecount=100000,in_len=16,out_len=16,migrateData=False):
    self.writeHead = 0
    self.tracecount = tracecount
    print("CaptureSet: debug, creating new captureset")
    self.samplecount=samplecount
    self.traces = None
    if migrateData is False:
      print("CaptureSet: sdr fix, self.traces is 0")
      # self.traces = np.zeros((tracecount,samplecount),np.float32)
      self.data_in = np.zeros((tracecount,in_len),np.uint8)
      self.data_out = np.zeros((tracecount,out_len),np.uint8)
    else:
      print("CaptureSet: migrating data, not creating trace sets")

  def addTrace(self,trace,data_in,data_out):
    if self.traces is None:
      self.traces = np.zeros((self.tracecount,self.samplecount),dtype=trace.dtype) 
    try:
      self.traces[self.writeHead:] = trace
    except ValueError:
      if len(trace) > self.traces.shape[1]:
        len_diff = len(trace) - self.traces.shape[1]
        print("Expanding trace array by %d" % len_diff)
        self.traces = np.pad(self.traces,((0,0),(0,len_diff)),"constant",constant_values=0) 
        self.traces[self.writeHead:] = trace
      elif len(trace) < self.traces.shape[1]:
        len_diff = self.traces.shape[1] - len(trace)
        print("Padding single trace by %d" % len_diff)
        trace = np.append(trace,np.zeros(len_diff,np.float32))
        self.traces[self.writeHead:] = trace
      else:
        print(len(trace))
        print(self.traces.shape)
        raise ValueError("Unknown ValueError exception, debugme (filemanager.py)")
    self.data_in[self.writeHead:] = data_in
    self.data_out[self.writeHead:] = data_out
    self.writeHead += 1

  def setConfig(self,cfgname,cfgval):
    print("CaptureSet: setting config value")
    if hasattr(self,"config_data"):
      self.config_data.append( "%s:%s" % (cfgname,cfgval)  )
      return True
    else:
      self.config_data = ["%s:%s" % (cfgname,cfgval)]
      return False

  def getConfig(self,cfgname):
    print("CaptureSet: getting config value")
    if hasattr(self,"config_data"):
      for x in self.config_data:
        try:
          (saved_cfgname,saved_cfgval) = x.split(":")
        except:
          print("CaptureSet: incorrect config data, '%s' is not 'cfg:val'" % x)
          return None
        if cfgname == saved_cfgname:
          print("CaptureSet: got config name '%s'" % cfgname)
          return saved_cfgval
      print("CaptureSet: missing config name '%s'" % cfgname)
      return None
    else:
      print("CaptureSet: no config data available")
      return None 

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
    if hasattr(self,"config_data"):
      print("CaptureSet: saving with extra config data")
      tn.f.create_dataset("config_data",data=self.config_data)

# class TraceSet:
#   def __init__(self,key):
#     print("TraceSet: Initialized blank TraceSet with key %s" % key)
#     self.key = key
#     self.dtype = None
#     self.traces = None
#     self.data = None
#     self.data_out = None

class TraceManager:
  def cleanup(self):
    print("TraceManager: saveBlock wrapping up")
    if self.f is not None:
      self.f.close()

  def getDtype(self):
    if len(self.traces) == 0:
      print("fatal: getDtype on empty trace array. dafuq?")
      return None
    if self.dtype is None:
      self.dtype = self.traces[0].dtype
    return self.dtype

  def slice(self,offset,numsamples):
    print("TraceManager: vertical slicing keeping %d:%d")
    if numsamples <= 0:
      print("TraceManager: numsamples must be positive nonzero")
      return
    if (offset <= 0) or (offset + numsamples >= self.numPoints):
      print("TraceManager: offset + numsamples must be less than %d" % self.numPoints)
      return
    newtraces = np.zeros((self.numTraces,numsamples),self.getDtype())
    for i in range(0,len(self.traces)):
      newtraces[i] = self.traces[i][offset:offset+numsamples]
    self.traces = newtraces
    self.numPoints = numsamples
    print("TraceManager: vertical slicing complete")

  # this needed to use weights in the old trace format, this is
  def getMeant(self):
    print("TraceManager2: getMeant called")
    m = numpy.mean(self.traces,axis=0)    
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
    self.tracesNew = np.zeros((self.traceCount,end - start),self.getDtype())
    for i in range(0,self.traceCount):
      # print(len(self.traces[i]))
      self.tracesNew[i] = self.traces[i,start:end]
    print("TraceManager2: Deleting previous trace set")
    del self.traces
    self.traces = self.tracesNew

  def randomSelect(self,samplesz):
    print("TraceManager2: Redrawing magic circle")
    print(np.random.choice(self.traces.shape[0], size = samplesz, replace=False))
    self.traces = self.traces[sorted(np.random.choice(self.traces.shape[0], size = samplesz, replace=False))]
    self.traceCount = len(self.traces)

  def __init__(self,filename_raw):
    if "~" in filename_raw:
      print("TraceManager2: attempting duct tape fix for user path")
      filename = os.path.expanduser(filename_raw)
    else:
      filename = filename_raw
    print("TraceManager2: Initializing with filename %s" % filename)
    self.fn = filename
    self.dtype = None
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
      if "config_data" in self.f.keys():
        print("TraceManager2: got config data, loading")
        self.config_data = self.f["config_data"]
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
  print("This file should not be called directly :)")
