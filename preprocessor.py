#!/usr/bin/env python3

import os
import scipy.io
from scipy.signal import butter,lfilter,freqz
from numpy import *
import getopt
import sys
import readline
import support.filemanager
import support.slipnslide
import support.preprocessor
import numpy as np
# import matplotlib.pyplot as plt
import pywt
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

def butter_bandpass(lowcut,highcut,fs,order=5):
  nyq = 0.5 * fs
  low = lowcut / nyq
  high = highcut / nyq
  b,a = butter(order, [low, high], btype = 'bandpass')
  return b,a

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
  return sum(abs(array1 - array2))

def getMaxCorrCoeff(trace1,trace2):
  maxCf = -1.0
  CONFIG_CLKADJUST_MAX = varMgr.getOptionalVariable("clkadjust_max",0)
  CONFIG_CLKADJUST = varMgr.getOptionalVariable("clkadjust",10000)
  CONFIG_WINDOW_OFFSET = varMgr.getVariable("window_offset")
  CONFIG_WINDOW_LENGTH = varMgr.getVariable("window_length")
  CONFIG_WINDOW_SLIDE = varMgr.getVariable("window_slide")
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
        try:
          r = corrcoef(r1,r2)
        except:
          continue
        if r[0,1] > maxCf:
          maxCf = r[0,1]
          maxCfIndex = i
      for i in range(-CONFIG_WINDOW_SLIDE,0):
        i += LOCAL_CLOCKADJUST
        r1 = trace1[CONFIG_WINDOW_OFFSET + i:CONFIG_WINDOW_OFFSET + CONFIG_WINDOW_LENGTH + i]
        r2 = trace2[CONFIG_WINDOW_OFFSET:CONFIG_WINDOW_OFFSET + CONFIG_WINDOW_LENGTH]
        try:
          r = corrcoef(r1,r2)
        except:
          continue
        # print(r)
        if r[0,1] > maxCf:
          maxCf = r[0,1]
          maxCfIndex = i
  return (maxCf,maxCfIndex)

def getMinimalSAD(trace1,trace2):
  minimalSAD = 1000.0
  minimalSADIndex = 0.0
  CONFIG_CLKADJUST_MAX = varMgr.getOptionalVariable("clkadjust_max",0)
  CONFIG_CLKADJUST = varMgr.getOptionalVariable("clkadjust",10000)
  CONFIG_WINDOW_OFFSET = varMgr.getVariable("window_offset")
  CONFIG_WINDOW_LENGTH = varMgr.getVariable("window_length")
  CONFIG_WINDOW_SLIDE = varMgr.getVariable("window_slide")
  for cadjust in range(0,CONFIG_CLKADJUST_MAX + 1):
    if cadjust == 0:
      cAdjustNeg = [0]
    else:
      cAdjustNeg = [cadjust * CONFIG_CLKADJUST, -cadjust * CONFIG_CLKADJUST]
    for LOCAL_CLOCKADJUST in cAdjustNeg:
      for i in range(0,CONFIG_WINDOW_SLIDE):
        i += LOCAL_CLOCKADJUST
        try:
          ms = getSingleSAD(trace1[CONFIG_WINDOW_OFFSET + i:CONFIG_WINDOW_OFFSET + CONFIG_WINDOW_LENGTH + i],trace2[CONFIG_WINDOW_OFFSET:CONFIG_WINDOW_OFFSET + CONFIG_WINDOW_LENGTH])
        except:
          continue
        if ms < minimalSAD:
          minimalSAD = ms
          minimalSADIndex = i
      for i in range(-CONFIG_WINDOW_SLIDE,0):
        i += LOCAL_CLOCKADJUST
        if CONFIG_WINDOW_OFFSET + i > 0:
          try:
            ms = getSingleSAD(trace1[CONFIG_WINDOW_OFFSET + i:CONFIG_WINDOW_OFFSET + CONFIG_WINDOW_LENGTH + i],trace2[CONFIG_WINDOW_OFFSET:CONFIG_WINDOW_OFFSET + CONFIG_WINDOW_LENGTH])
          except:
            continue
          if ms < minimalSAD:
            minimalSAD = ms
            minimalSADIndex = i
  return (minimalSADIndex,minimalSAD)

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
      print("Could not retrieve variable '%s', supplying default" % var)
      return opt

varMgr = VariableManager()

def doCORR(tm_in):
  numTraces = tm_in.traceCount
  sampleCnt = tm_in.numPoints
  traces = zeros((numTraces,sampleCnt),float32)
  data = zeros((numTraces,16),uint8)
  data_out = zeros((numTraces,16),uint8)
  CONFIG_REFTRACE = varMgr.getVariable("ref")
  CONFIG_LOWPASS = varMgr.getOptionalVariable("lowpass",None)
  CONFIG_MCF_CUTOFF = varMgr.getVariable("corr_cutoff")
  CONFIG_WINDOW_SLIDE = varMgr.getVariable("window_slide")
  CONFIG_WRITEFILE = varMgr.getVariable("writefile")
  savedDataIndex = 0
  if CONFIG_LOWPASS is not None:
    (CONFIG_CUTOFF,CONFIG_SAMPLERATE,CONFIG_ORDER) = varMgr.getOptionalVariable("lowpass",None)
    ref = butter_lowpass_filter(tm_in.getSingleTrace(CONFIG_REFTRACE),CONFIG_CUTOFF,CONFIG_SAMPLERATE,CONFIG_ORDER)
  else:
    ref = tm_in.getSingleTrace(CONFIG_REFTRACE)
  for i in range(0,numTraces):
    x = tm_in.getSingleTrace(i)
    if CONFIG_LOWPASS is not None:
      r2 = butter_lowpass_filter(x,CONFIG_CUTOFF,CONFIG_SAMPLERATE,CONFIG_ORDER)
    else:
      r2 = x
    (msv,msi) = getMaxCorrCoeff(r2,ref)
    if msv > CONFIG_MCF_CUTOFF:
      # if msi == -CONFIG_WINDOW_SLIDE or msi == CONFIG_WINDOW_SLIDE - 1:
      #   print(("Index %d, discarding (edge Max Coeff Index = not found, mcf is %f)" % (i,msv)))
      if True:
        print(("Index %d, Max Corr Coeff Slide %d Samples, Max CF Value %f" % (i,msi,msv)))
        # traces[savedDataIndex,:] = roll(x,msi)
        traces[savedDataIndex,:] = roll(x,-msi)
        data[savedDataIndex,:] = tm_in.getSingleData(i)
        data_out[savedDataIndex,:] = tm_in.getSingleDataOut(i)
        savedDataIndex += 1
    else:
      print(("Index %d, discarding (correlation is %f, index is %d)" % (i,msv,msi)))
  print("Returning data, don't forget to commit!")
  return (traces[0:savedDataIndex],data[0:savedDataIndex],data_out[0:savedDataIndex])
  # print("Saving...")
  # support.filemanager.save(CONFIG_WRITEFILE,traces=traces[0:savedDataIndex],data=data[0:savedDataIndex],data_out=data_out[0:savedDataIndex])

import copy
def doSingleCWTDenoise(x,wavelet="db4",level=1):
  # x = copy.copy(x_in) # lol wtf
  coeff = pywt.wavedec(x,wavelet,mode="per")
  sigma = mad( coeff[-level])
  uthresh = sigma * np.sqrt( 2 * np.log( len(x) ) )
  coeff[1:] = (pywt.threshold(i,value=uthresh,mode="soft") for i in coeff[1:])
  y = pywt.waverec(coeff,wavelet,mode="per")
  # del(x)
  return y
  
from statsmodels.robust import mad
def doCWTDenoise(tm_in):
  numTraces = tm_in.traceCount
  sampleCnt = tm_in.numPoints
  traces = zeros((numTraces,sampleCnt),float32)
  data = zeros((numTraces,16),uint8)
  data_out = zeros((numTraces,16),uint8)
  savedDataIndex = 0
  CONFIG_WRITEFILE = varMgr.getVariable("writefile")
  for i in range(0,numTraces):
    x = tm_in.getSingleTrace(i)
    dn = doSingleCWTDenoise(tm_in.getSingleTrace(i))
    if isnan(dn[0]):
      print("Discarding trace %d" % i)
    else:
      print("De-noised trace %d..." % i)
      traces[savedDataIndex,:] = dn
      data[savedDataIndex,:] = tm_in.getSingleData(i)
      data_out[savedDataIndex,:] = tm_in.getSingleDataOut(i)
      savedDataIndex += 1
  print("Returning data, don't forget to commit!")
  return (traces[0:savedDataIndex],data[0:savedDataIndex],data_out[0:savedDataIndex])
  # print("Saving...")
  # support.filemanager.save(CONFIG_WRITEFILE,traces=traces[0:savedDataIndex],data=data[0:savedDataIndex],data_out=data_out[0:savedDataIndex])

def unpackKeeloq(plaintext):
  out = ""
  for i in range(0,9):
    out = format(plaintext[i],"08b") + out
  return out
  # return out[6:]

def packKeeloq(bitstring):
  bs = int(bitstring,2)
  out = [0] * 16
  for i in range(0,9):
    fq = (bs >> (i * 8)) & 0xFF
    out[i] = fq
  return out

def doFlipKeeloqIO(tm_in):
  numTraces = tm_in.traceCount
  sampleCnt = tm_in.numPoints
  traces = zeros((numTraces,sampleCnt),float32)
  data = zeros((numTraces,16),uint8)
  data_out = zeros((numTraces,16),uint8)
  savedDataIndex = 0
  CONFIG_WRITEFILE = varMgr.getVariable("writefile")
  for i in range(0,numTraces):
    print("Flipping IO for trace %d..." % i)
    traces[savedDataIndex,:] = tm_in.getSingleTrace(i)
    # print(unpackKeeloq(tm_in.getSingleData(i))[::-1])
    # print(packKeeloq(unpackKeeloq(tm_in.getSingleData(i))[::-1]))
    # sys.exit(0)
    data[savedDataIndex,:] = packKeeloq(unpackKeeloq(tm_in.getSingleData(i))[::-1])
    data_out[savedDataIndex,:] = packKeeloq(unpackKeeloq(tm_in.getSingleDataOut(i)[::-1])[::-1])
    savedDataIndex += 1
  print("Returning data, don't forget to commit!")
  return (traces[0:savedDataIndex],data[0:savedDataIndex],data_out[0:savedDataIndex])
  # print("Saving...")
  # support.filemanager.save(CONFIG_WRITEFILE,traces=traces[0:savedDataIndex],data=data[0:savedDataIndex],data_out=data_out[0:savedDataIndex])

def doLowpass(tm_in):
  numTraces = tm_in.traceCount
  sampleCnt = tm_in.numPoints
  traces = zeros((numTraces,sampleCnt),float32)
  data = zeros((numTraces,16),uint8)
  data_out = zeros((numTraces,16),uint8)
  savedDataIndex = 0
  CONFIG_WRITEFILE = varMgr.getVariable("writefile")
  (CONFIG_LCUTOFF,CONFIG_SAMPLERATE,CONFIG_ORDER) = varMgr.getOptionalVariable("lowpass",None)
  for i in range(0,numTraces):
    print("Lowpassed traced %d..." % i)
    x = tm_in.getSingleTrace(i)
    r2 = butter_lowpass_filter(x,CONFIG_LCUTOFF,CONFIG_SAMPLERATE,CONFIG_ORDER)
    traces[savedDataIndex,:] = r2
    data[savedDataIndex,:] = tm_in.getSingleData(i)
    data_out[savedDataIndex,:] = tm_in.getSingleDataOut(i)
    savedDataIndex += 1
  print("Returning data, don't forget to commit!")
  return (traces[0:savedDataIndex],data[0:savedDataIndex],data_out[0:savedDataIndex])
  # print("Saving...")
  # support.filemanager.save(CONFIG_WRITEFILE,traces=traces[0:savedDataIndex],data=data[0:savedDataIndex],data_out=data_out[0:savedDataIndex])

def doBandpass(tm_in):
  numTraces = tm_in.traceCount
  sampleCnt = tm_in.numPoints
  traces = zeros((numTraces,sampleCnt),float32)
  data = zeros((numTraces,16),uint8)
  data_out = zeros((numTraces,16),uint8)
  savedDataIndex = 0
  CONFIG_WRITEFILE = varMgr.getVariable("writefile")
  (CONFIG_LCUTOFF,CONFIG_HCUTOFF,CONFIG_SAMPLERATE,CONFIG_ORDER) = varMgr.getOptionalVariable("bandpass",None)
  for i in range(0,numTraces):
    print("Bandpassed traced %d..." % i)
    x = tm_in.getSingleTrace(i)
    r2 = butter_bandpass_filter(x,CONFIG_LCUTOFF,CONFIG_HCUTOFF,CONFIG_SAMPLERATE,CONFIG_ORDER)
    traces[savedDataIndex,:] = r2
    data[savedDataIndex,:] = tm_in.getSingleData(i)
    data_out[savedDataIndex,:] = tm_in.getSingleDataOut(i)
    savedDataIndex += 1
  print("Returning data, don't forget to commit!")
  return (traces[0:savedDataIndex],data[0:savedDataIndex],data_out[0:savedDataIndex])
  # print("Saving...")
  # support.filemanager.save(CONFIG_WRITEFILE,traces=traces[0:savedDataIndex],data=data[0:savedDataIndex],data_out=data_out[0:savedDataIndex])

def doEarthquake(tm_in):
  numTraces = tm_in.traceCount
  sampleCnt = tm_in.numPoints
  traces = zeros((numTraces,sampleCnt),float32)
  data = zeros((numTraces,16),uint8)
  data_out = zeros((numTraces,16),uint8)
  CONFIG_WRITEFILE = varMgr.getVariable("writefile")
  CONFIG_SLIDEAMOUNT = int(varMgr.getOptionalVariable("slidemax",1500))
  savedDataIndex = 0
  for i in range(0,numTraces):
    x = tm_in.getSingleTrace(i)
    rval = int(-(CONFIG_SLIDEAMOUNT)) + random.randint(0,CONFIG_SLIDEAMOUNT * 2)
    print(("Index %d, rolling %d!" % (i,rval)))
    traces[savedDataIndex,:] = roll(x,rval)
    data[savedDataIndex,:] = tm_in.getSingleData(i)
    data_out[savedDataIndex,:] = tm_in.getSingleDataOut(i)
    savedDataIndex += 1
  print("Returning data, don't forget to commit!")
  return (traces[0:savedDataIndex],data[0:savedDataIndex],data_out[0:savedDataIndex])
  # print("Saving...")
  # support.filemanager.save(CONFIG_WRITEFILE,traces=traces[0:savedDataIndex],data=data[0:savedDataIndex],data_out=data_out[0:savedDataIndex])

def doSlicer(tm_in):
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
  traces = zeros((numTraces,newSampleCount),float32)
  data = zeros((numTraces,16),uint8)
  data_out = zeros((numTraces,16),uint8)
  numTraces = tm_in.traceCount
  se = support.slipnslide.SliceEngine(tm_in)
  for i in range(0,numTraces):
    print("Slicing trace %d" % i)
    traces[i:] = se.FindSlices(i, CONFIG_REF_OFFSET, CONFIG_REF_LENGTH,CONFIG_SLICE_DIST,CONFIG_SAD_CUTOFF,maxSlicesBackwards,maxSlicesForwards)
    data[i,:] = tm_in.getSingleData(i)
    data_out[i,:] = tm_in.getSingleDataOut(i)
  print("Returning data, don't forget to commit!")
  return (traces,data,data_out)
  # support.filemanager.save(CONFIG_WRITEFILE,traces=traces,data=data,data_out=data_out)

def doVerticalAlign(tm_in):
  numTraces = tm_in.traceCount
  sampleCnt = tm_in.numPoints
  traces = zeros((numTraces,sampleCnt),float32)
  data = zeros((numTraces,16),uint8)
  data_out = zeros((numTraces,16),uint8)
  CONFIG_REFTRACE = varMgr.getVariable("ref")
  ref = tm_in.getSingleTrace(CONFIG_REFTRACE)

def doSAD(tm_in):
  numTraces = tm_in.traceCount
  sampleCnt = tm_in.numPoints
  traces = zeros((numTraces,sampleCnt),float32)
  data = zeros((numTraces,16),uint8)
  data_out = zeros((numTraces,16),uint8)
  CONFIG_REFTRACE = varMgr.getVariable("ref")
  CONFIG_LOWPASS = varMgr.getOptionalVariable("lowpass",None)
  CONFIG_SAD_CUTOFF = varMgr.getVariable("sad_cutoff")
  CONFIG_WRITEFILE = varMgr.getVariable("writefile")
  CONFIG_WINDOW_SLIDE = varMgr.getVariable("window_slide")
  savedDataIndex = 0
  if CONFIG_LOWPASS is not None:
    (CONFIG_CUTOFF,CONFIG_SAMPLERATE,CONFIG_ORDER) = varMgr.getOptionalVariable("lowpass",None)
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
        # traces[savedDataIndex,:] = roll(x,msi)
        data[savedDataIndex,:] = tm_in.getSingleData(i)
        data_out[savedDataIndex,:] = tm_in.getSingleDataOut(i)
        savedDataIndex += 1
    else:
      print(("Index %d, discarding (MSV is %f)" % (i,msv)))
  print("Returning data, don't forget to commit!")
  return (traces[0:savedDataIndex],data[0:savedDataIndex],data_out[0:savedDataIndex])
  # support.filemanager.save(CONFIG_WRITEFILE,traces=traces[0:savedDataIndex],data=data[0:savedDataIndex],data_out=data_out[0:savedDataIndex])

def dispatchAlign(tm_in):
  CONFIG_STRATEGY = varMgr.getVariable("strategy")
  if CONFIG_STRATEGY in ("sad","SAD"):
    print("Using strategy: Align by Sum of Absolute Differences")
    (traces,data_in,data_out) = doSAD(tm_in)
  elif CONFIG_STRATEGY in ("earthquake","EARTHQUAKE"):
    print("Using strategy: Misalign by time-quake! Yay for testing!")
    (traces,data_in,data_out) = doEarthquake(tm_in)
  elif CONFIG_STRATEGY in ("corr","CORR"):
    print("Using strategy: Align by Maximum Correlation")
    (traces,data_in,data_out) = doCORR(tm_in)
  elif CONFIG_STRATEGY.upper() == "VALIGN":
    (traces,data_in,data_out) = support.preprocessor.VAlign(tm_in,varMgr)
  elif CONFIG_STRATEGY in ("wavelet","WAVELET"):
    print("Using strategy: Wavelet Denoise")
    (traces,data_in,data_out) = doCWTDenoise(tm_in)
  elif CONFIG_STRATEGY in ("bandpass","BANDPASS"):
    print("Using strategy: Band Pass")
    (traces,data_in,data_out) = doBandpass(tm_in)
  elif CONFIG_STRATEGY in ("lowpass","LOWPASS"):
    print("Using strategy: Low Pass")
    (traces,data_in,data_out) = doLowpass(tm_in)
  elif CONFIG_STRATEGY in ("vertical","VERTICAL"):
    print("Using strategy: Vertical Align")
    (traces,data_in,data_out) = doVerticalAlign(tm_in)
  elif CONFIG_STRATEGY in ("keeloq","KEELOQ"):
    print("Using strategy: Flip Keeloq IO Special")
    (traces,data_in,data_out) = doFlipKeeloqIO(tm_in)
  elif CONFIG_STRATEGY.upper() == "SLICER":
    print("Using strategy: SlipNSlide Slice Extractor")
    (traces,data_in,data_out) = doSlicer(tm_in)
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
    varMgr.unset(argname)
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
    return tm_in_new
  elif tokens[0] in ["c","commit"]:
    if needsCommit:
      support.filemanager.save(CONFIG_WRITEFILE,traces=tm_in.traces,data=tm_in.data_in,data_out=tm_in.data_out) 
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
  tm_in = support.filemanager.TraceManager(CONFIG_READFILE)
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
    doSingleCommand(cmd,tm_in)

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


