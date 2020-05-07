#!/usr/bin/env python3

import os
import scipy.io
from scipy.signal import butter,lfilter,freqz
from numpy import *
import getopt
import sys
import support.filemanager
import numpy as np
import matplotlib.pyplot as plt

def butter_bandpass(lowcut,highcut,fs,order=5):
  nyq = 0.5 * fs
  low = lowcut / nyq
  high = highcut / nyq
  b,a = butter(order, [low, high], btype = 'band')

def butter_bandpass_filter(data,lowcut,highcut,fs,order=5):
  b,a = butter_bandpass(lowcut,highcut,fs,order=order)
  y = lfilter(b,a,data)
  return y

def butter_lowpass(cutoff, fs, order=5):
  nyq = 0.5 * fs
  normal_cutoff = cutoff / nyq
  b, a = butter(order, normal_cutoff, btype='low', analog=False)
  return b, a

def butter_lowpass_filter(data, cutoff, fs, order=5):
  b, a = butter_lowpass(cutoff, fs, order=order)
  y = lfilter(b, a, data)
  return y

def getSingleSAD(array1,array2):
  totalSAD = 0.0
  return sum(abs(abs(array1) - abs(array2)))

def getMaxCorrCoeff(trace1,trace2):
  maxCf = -1.0
  maxCfIndex = 0
  for cadjust in range(0,CONFIG_CLKADJUST_MAX + 1):
    if cadjust == 0:
      cAdjustNeg = [0]
    else:
      cAdjustNeg = [cadjust * CONFIG_CLKADJUST, -cadjust * CONFIG_CLKADJUST]
    for LOCAL_CLOCKADJUST in cAdjustNeg:
      for i in range(0,CONFIG_WINDOW_SLIDE):
        i += LOCAL_CLOCKADJUST
        r1 = trace1[CONFIG_WINDOW_OFFSET + i:CONFIG_WINDOW_OFFSET + CONFIG_WINDOW_LENGTH + i]
        r2 = trace2[CONFIG_WINDOW_OFFSET:CONFIG_WINDOW_OFFSET + CONFIG_WINDOW_LENGTH]
        r = corrcoef(r1,r2)
        if r[0,1] > maxCf:
          maxCf = r[0,1]
          maxCfIndex = i
      for i in range(-CONFIG_WINDOW_SLIDE,0):
        i += LOCAL_CLOCKADJUST
        r1 = trace1[CONFIG_WINDOW_OFFSET + i:CONFIG_WINDOW_OFFSET + CONFIG_WINDOW_LENGTH + i]
        r2 = trace2[CONFIG_WINDOW_OFFSET:CONFIG_WINDOW_OFFSET + CONFIG_WINDOW_LENGTH]
        r = corrcoef(r1,r2)
        # print(r)
        if r[0,1] > maxCf:
          maxCf = r[0,1]
          maxCfIndex = i
  return (maxCf,maxCfIndex)

def getMinimalSAD(trace1,trace2):
  minimalSAD = 500.0
  minimalSADIndex = 0.0
  CONFIG_CLKADJUST_MAX = getOptionalVariable("clkadjust_max",0)
  CONFIG_CLKADJUST = getOptionalVariable("clkadjust",10000)
  CONFIG_WINDOW_OFFSET = getVariable("window_offset")
  CONFIG_WINDOW_LENGTH = getVariable("window_length")
  CONFIG_WINDOW_SLIDE = getVariable("window_slide")
  for cadjust in range(0,CONFIG_CLKADJUST_MAX + 1):
    if cadjust == 0:
      cAdjustNeg = [0]
    else:
      cAdjustNeg = [cadjust * CONFIG_CLKADJUST, -cadjust * CONFIG_CLKADJUST]
    for LOCAL_CLOCKADJUST in cAdjustNeg:
      for i in range(0,CONFIG_WINDOW_SLIDE):
        i += LOCAL_CLOCKADJUST
        ms = getSingleSAD(trace1[CONFIG_WINDOW_OFFSET + i:CONFIG_WINDOW_OFFSET + CONFIG_WINDOW_LENGTH + i],trace2[CONFIG_WINDOW_OFFSET:CONFIG_WINDOW_OFFSET + CONFIG_WINDOW_LENGTH])
        if ms < minimalSAD:
          minimalSAD = ms
          minimalSADIndex = i
      for i in range(-CONFIG_WINDOW_SLIDE,0):
        i += LOCAL_CLOCKADJUST
        if CONFIG_WINDOW_OFFSET + i > 0:
          ms = getSingleSAD(trace1[CONFIG_WINDOW_OFFSET + i:CONFIG_WINDOW_OFFSET + CONFIG_WINDOW_LENGTH + i],trace2[CONFIG_WINDOW_OFFSET:CONFIG_WINDOW_OFFSET + CONFIG_WINDOW_LENGTH])
          if ms < minimalSAD:
            minimalSAD = ms
            minimalSADIndex = i
  return (minimalSADIndex,minimalSAD)

CFG_GLOBALS = {}

def requireTokens(tokens):
  global CFG_GLOBALS
  for t in tokens:
    if t not in CFG_GLOBALS.keys():
      return False
  return True

def getOptionalVariable(varname, default):
  global CFG_GLOBALS
  if varname not in CFG_GLOBALS.keys():
    print("Could not retrieve variable '%s'" % varname)
    return default
  else:
    return CFG_GLOBALS[varname]

def getVariable(varname):
  global CFG_GLOBALS
  if varname not in CFG_GLOBALS.keys():
    print("Could not retrieve mandatory variable '%s'" % varname)
    sys.exit(0)
  else:
    return CFG_GLOBALS[varname]

def getLowpass():
  global CFG_GLOBALS
  if "lowpass" not in CFG_GLOBALS.keys():
    return None
  else:
    return CFG_GLOBALS["lowpass"]

def doSAD(tm_in,CONFIG_WRITEFILE):
  numTraces = tm_in.traceCount
  sampleCnt = tm_in.numPoints
  traces = zeros((numTraces,sampleCnt),float32)
  data = zeros((numTraces,16),uint8)
  data_out = zeros((numTraces,16),uint8)
  CONFIG_REFTRACE = getVariable("ref")
  CONFIG_LOWPASS = getLowpass()
  CONFIG_SAD_CUTOFF = getVariable("sad_cutoff")
  CONFIG_WINDOW_SLIDE = getVariable("window_slide")
  savedDataIndex = 0
  if CONFIG_LOWPASS is not None:
    (CONFIG_CUTOFF,CONFIG_SAMPLERATE,CONFIG_ORDER) = getLowpass()
    ref = butter_lowpass_filter(tm_in.getSingleTrace(CONFIG_REFTRACE),CONFIG_CUTOFF,CONFIG_SAMPLERATE,CONFIG_ORDER)
  else:
    ref = tm_in.getSingleTrace(CONFIG_REFTRACE)
  print("Reference trace fetched, go.")
  for i in range(0,numTraces):
    x = tm_in.getSingleTrace(i)
    if CONFIG_LOWPASS is not None:
      r2 = butter_lowpass_filter(x,CONFIG_CUTOFF,CONFIG_SAMPLERATE,CONFIG_ORDER)
    else:
      r2 = x
    (msi,msv) = getMinimalSAD(r2,ref)
    if msv < CONFIG_SAD_CUTOFF:
      if msi == -CONFIG_WINDOW_SLIDE or msi == CONFIG_WINDOW_SLIDE - 1:
        print(("Index %d, discarding (edge MSI = not found)" % i))
      else:
        print(("Index %d, Minimal SAD Slide %d Samples, Minimal SAD Value %f" % (i,msi,msv)))
        # traces[savedDataIndex,:] = x
        traces[savedDataIndex,:] = roll(x,-msi)
        data[savedDataIndex,:] = tm_in.getSingleData(i)
        data_out[savedDataIndex,:] = tm_in.getSingleDataOut(i)
        savedDataIndex += 1
    else:
      print(("Index %d, discarding (MSV is %f)" % (i,msv)))
  print("Saving...")
  support.filemanager.save(CONFIG_WRITEFILE,traces=traces[0:savedDataIndex],data=data[0:savedDataIndex],data_out=data_out[0:savedDataIndex])

def dispatchAlign(tm_in,CONFIG_WRITEFILE):
  global CFG_GLOBALS
  if CFG_GLOBALS["strategy"] in ("sad","SAD"):
    print("Using strategy: SAD")
    doSAD(tm_in,CONFIG_WRITEFILE)
  elif CFG_GLOBALS["strategy"] in ("corr","CORR"):
    print("Using strategy: Correlation (not implemented)")
  else:
    print("Strategy must be one of SAD, CORR")
    return

def doSingleCommand(cmd,tm_in,CONFIG_WRITEFILE):
  tokens = cmd.split(" ")
  if tokens[0] == "set" and len(tokens) >= 2:
    tx = " ".join(tokens[1:])
    (argname,argval) = tx.split("=")
    CFG_GLOBALS[argname] = eval(argval)
  elif tokens[0] == "vars":
    for k in CFG_GLOBALS.keys():
      print("%s=%s" % (k,CFG_GLOBALS[k]))
  elif tokens[0] in ("r","run"):
    dispatchAlign(tm_in,CONFIG_WRITEFILE)
  elif tokens[0] in ("q","quit"):
    print("Bye!")
    sys.exit(0)
  else:
    print("Unknown / invalid command")

def doCommands(CONFIG_READFILE,CONFIG_WRITEFILE,CONFIG_CMDFILE):
  global CFG_GLOBALS
  tm_in = support.filemanager.TraceManager(CONFIG_READFILE)
  if CONFIG_CMDFILE is not None:
    f = open(CONFIG_CMDFILE)
    cmds = [d.rstrip() for d in f.readlines()]
    for i in range(0,len(cmds)):
      doSingleCommand(cmds[i],tm_in,CONFIG_WRITEFILE)
  while True:
    cmd = input(" > ").lstrip().rstrip()
    doSingleCommand(cmd,tm_in,CONFIG_WRITEFILE)

if __name__ == "__main__":
  CONFIG_READFILE = None
  CONFIG_WRITEFILE = None
  CONFIG_CMDFILE = None
  args, opts = getopt.getopt(sys.argv[1:],"f:w:c:",["infile=","writefile=","cmdfile="])
  for arg,opt in args:
    if arg in ("-f","--infile"):
      CONFIG_READFILE = opt
    elif arg in ("-w","--writefile"):
      CONFIG_WRITEFILE = opt
    elif arg in ("-c","--cmdfile"):
      CONFIG_CMDFILE = opt
  if CONFIG_READFILE is None or CONFIG_WRITEFILE is None:
    print("You must specify both -r and -w")
    sys.exit(0)
  if os.path.isfile(CONFIG_READFILE) is False:
    print("Source file %s not valid" % CONFIG_READFILE)
    sys.exit(0)
  doCommands(CONFIG_READFILE,CONFIG_WRITEFILE,CONFIG_CMDFILE)

sys.exit(0)
