#!/usr/bin/env python3

import os
import scipy.io
from numpy import *
import getopt
import sys
import readline
import sparkgap.filemanager
import sparkgap.slipnslide
import sparkgap.preprocessor
import sparkgap.preprocessor.sdr
import sparkgap.preprocessor.filtering
import sparkgap.preprocessor.alignment
import sparkgap.preprocessor.keeloq
import sparkgap.preprocessor.slicer
import numpy as np
import random

class TraceManagerStub:
  def __init__(self,traces,data_in,data_out):
    print("TraceManagerStub: Creating with %d traces" % len(traces))
    self.traces = traces
    self.data_in = data_in
    self.data_out = data_out
    self.traceCount = len(self.traces)
    self.numPoints = len(self.traces[0])

  def getSingleTrace(self,i):
    return self.traces[i]

  def getSingleData(self,i):
    return self.data_in[i]

  def getSingleDataOut(self,i):
    return self.data_out[i]

CFG_OPTIONAL_WARNINGS = []

class VariableManager:
  def __init__(self):
    self.config = {}

  def list(self):
    for k in self.config.keys():
      print("%s=%s" % (k,self.config[k]))

  def unset(self,var):
    if var in self.config.keys():
      del self.config[var]
 
  def setVariable(self,var,arg):
    self.config[var] = arg

  def getVariable(self,var):
    return self.config[var]

  def getOptionalVariable(self,var,opt):
    if var in self.config.keys():
      return self.config[var]
    else:
      print("Could not retrieve variable '%s', supplying default (once only)" % var)
      self.config[var] = opt
      return opt

varMgr = VariableManager()

dispatchLookup = {}
dispatchLookup["sad"] = ("Align by sum of absolute differences",sparkgap.preprocessor.alignment.doSAD)
dispatchLookup["earthquake"] = ("Horizontal misalign",sparkgap.preprocessor.alignment.doEarthquake)
dispatchLookup["corr"] = ("Align by Pearson correlation",sparkgap.preprocessor.alignment.doCORR)
dispatchLookup["valign"] = ("Vertical align",sparkgap.preprocessor.VAlign)
dispatchLookup["two_point_compress"] = ("Difference-of-Two-Points Compress (needs compress_dist)",sparkgap.preprocessor.TwoPointCompress)
dispatchLookup["wavelet"] = ("Wavelet transform denoise",sparkgap.preprocessor.filtering.doCWTDenoise)
dispatchLookup["bandpass"] = ("Band pass filter",sparkgap.preprocessor.filtering.doBandpass)
dispatchLookup["lowpass"] = ("Low pass filter",sparkgap.preprocessor.filtering.doLowpass)
dispatchLookup["keeloq"] = ("Flip Keeloq IO Special",sparkgap.preprocessor.keeloq.doFlipKeeloqIO)
dispatchLookup["slicer"] = ("Signal slicer",sparkgap.preprocessor.slicer.doSlicer)
dispatchLookup["c2f"] = ("Complex to Float Conversion",sparkgap.preprocessor.sdr.complex2Float)

def dispatchAlign(tm_in):
  CONFIG_STRATEGY = varMgr.getVariable("strategy").lower()
  if CONFIG_STRATEGY in dispatchLookup.keys():
    (strategyName,strategyRun) = dispatchLookup[CONFIG_STRATEGY]
    print("Using strategy: %s" % strategyName)
    (traces,data_in,data_out) = strategyRun(tm_in,varMgr)
  else:
    print("Unknown strategy: %s" % CONFIG_STRATEGY)
    return (None,None,None)
  return (traces,data_in,data_out)

needsCommit = False

def doSingleCommand(cmd,tm_in_raw):
  global needsCommit
  CONFIG_WRITEFILE = varMgr.getVariable("writefile")
  tm_in = tm_in_raw
  tokens = cmd.split(" ")
  if tokens[0] == "set" and len(tokens) >= 2:
    tx = " ".join(tokens[1:])
    (argname,argval) = tx.split("=")
    varMgr.setVariable(argname,eval(argval))
  elif tokens[0] == "unset" and len(tokens) == 2:
    varMgr.unset(tokens[1])
  elif tokens[0] == "vars":
    varMgr.list()
  elif tokens[0] == "savecw":
    if needsCommit:
      print("Commit your changes first. No operation performed")
    else:
      print("Saving as ChipWhisperer format...")
      tm_in.save_cw()
    return None
  elif tokens[0] in ["rem","#",";","//"]:
    pass
    return None
  elif tokens[0] in ["r","run"]:
    (traces,data_in,data_out) = dispatchAlign(tm_in)
    needsCommit = True
    tm_in_new = TraceManagerStub(traces,data_in,data_out)
    print("tm_in should be replaced")
    return tm_in_new
  elif tokens[0] in ["c","commit"]:
    if needsCommit:
      s = sparkgap.filemanager.CaptureSet(migrateData  = True)
      s.tracecount = len(tm_in.traces)
      s.writeHead = s.tracecount
      print("Converted %d traces" % s.tracecount)
      s.traces   = tm_in.traces
      s.data_in  = tm_in.data_in
      s.data_out = tm_in.data_out
      s.save(CONFIG_WRITEFILE)
      # sparkgap.filemanager.save(CONFIG_WRITEFILE,traces=tm_in.traces,data=tm_in.data_in,data_out=tm_in.data_out) 
      needsCommit = False
    else:
      print("No changes need committing")
    return None
  elif tokens[0] == "force-quit":
    if needsCommit:
      print("Unsaved changes present, quitting anyway")
    print("Bye!")
    sys.exit(0)
  elif tokens[0] in ["q","quit"]:
    if needsCommit:
      print("Unsaved changes need committing, use 'force-quit' to quit without saving")
    else:
      print("Bye!")
      sys.exit(0)
  elif len(cmd) == 0:
    pass
    return None
  else:
    print("Unknown / invalid command")
    return None

def doCommands(CONFIG_READFILE,CONFIG_CMDFILE):
  tm_in = sparkgap.filemanager.TraceManager(CONFIG_READFILE)
  if CONFIG_CMDFILE is not None:
    f = open(CONFIG_CMDFILE)
    cmds = [d.rstrip() for d in f.readlines()]
    for i in range(0,len(cmds)):
      p = doSingleCommand(cmds[i],tm_in)
      if p is not None:
        print("doCommands loop: Replacing tm_in")
        tm_in = p
  while True:
    cmd = input(" > ").lstrip().rstrip()
    p = doSingleCommand(cmd,tm_in)
    if p is not None:
      print("doCommands loop: Replacing tm_in")
      tm_in = p

if __name__ == "__main__":
  CONFIG_READFILE = None
  CONFIG_CMDFILE = None
  args, opts = getopt.getopt(sys.argv[1:],"f:w:c:",["infile=","writefile=","cmdfile="])
  for arg,opt in args:
    if arg in ("-f","--infile"):
      CONFIG_READFILE = opt
    elif arg in ("-w","--writefile"):
      varMgr.setVariable("writefile",opt)
    elif arg in ("-c","--cmdfile"):
      CONFIG_CMDFILE = opt
  if CONFIG_READFILE is None:
    print("You must specify an input file with -f / --infile")
    sys.exit(0)
  if os.path.isfile(CONFIG_READFILE) is False:
    print("Source file %s not valid" % CONFIG_READFILE)
    sys.exit(0)
  doCommands(CONFIG_READFILE,CONFIG_CMDFILE)


