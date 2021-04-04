#!/usr/bin/env python3

import os
import scipy.io
from scipy.signal import butter,lfilter,freqz
from numpy import *
import getopt
import sys
import support.filemanager
import support.slipnslide
import numpy as np
import matplotlib.pyplot as plt
import pywt
import random

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
  CONFIG_CLKADJUST_MAX = getOptionalVariable("clkadjust_max",0)
  CONFIG_CLKADJUST = getOptionalVariable("clkadjust",10000)
  CONFIG_WINDOW_OFFSET = getVariable("window_offset")
  CONFIG_WINDOW_LENGTH = getVariable("window_length")
  CONFIG_WINDOW_SLIDE = getVariable("window_slide")
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
          contiune
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

CFG_GLOBALS = {}
CFG_OPTIONAL_WARNINGS = []

def requireTokens(tokens):
  global CFG_GLOBALS
  for t in tokens:
    if t not in CFG_GLOBALS.keys():
      return False
  return True

def getOptionalVariable(varname, default):
  global CFG_GLOBALS, CFG_OPTIONAL_WARNINGS
  if varname not in CFG_GLOBALS.keys():
    if varname not in CFG_OPTIONAL_WARNINGS:
      print("Could not retrieve variable '%s'" % varname)
      CFG_OPTIONAL_WARNINGS.append(varname)
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

def getBandpass():
  global CFG_GLOBALS
  if "bandpass" not in CFG_GLOBALS.keys():
    return None
  else:
    return CFG_GLOBALS["bandpass"]

def doCORR(tm_in):
  numTraces = tm_in.traceCount
  sampleCnt = tm_in.numPoints
  traces = zeros((numTraces,sampleCnt),float32)
  data = zeros((numTraces,16),uint8)
  data_out = zeros((numTraces,16),uint8)
  CONFIG_REFTRACE = getVariable("ref")
  CONFIG_LOWPASS = getLowpass()
  CONFIG_MCF_CUTOFF = getVariable("corr_cutoff")
  CONFIG_WINDOW_SLIDE = getVariable("window_slide")
  CONFIG_WRITEFILE = getVariable("writefile")
  savedDataIndex = 0
  if CONFIG_LOWPASS is not None:
    (CONFIG_CUTOFF,CONFIG_SAMPLERATE,CONFIG_ORDER) = getLowpass()
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
      if msi == -CONFIG_WINDOW_SLIDE or msi == CONFIG_WINDOW_SLIDE - 1:
        print(("Index %d, discarding (edge Max Coeff Index = not found, mcf is %f)" % (i,msv)))
      else:
        print(("Index %d, Max Corr Coeff Slide %d Samples, Max CF Value %f" % (i,msi,msv)))
        # traces[savedDataIndex,:] = roll(x,msi)
        traces[savedDataIndex,:] = roll(x,-msi)
        data[savedDataIndex,:] = tm_in.getSingleData(i)
        data_out[savedDataIndex,:] = tm_in.getSingleDataOut(i)
        savedDataIndex += 1
    else:
      print(("Index %d, discarding (correlation is %f, index is %d)" % (i,msv,msi)))
  print("Saving...")
  support.filemanager.save(CONFIG_WRITEFILE,traces=traces[0:savedDataIndex],data=data[0:savedDataIndex],data_out=data_out[0:savedDataIndex])

import copy
def doSingleCWTDenoise(x_in,wavelet="db4",level=1):
  x = copy.copy(x_in)
  coeff = pywt.wavedec(x,wavelet,mode="per")
  sigma = mad( coeff[-level])
  uthresh = sigma * np.sqrt( 2 * np.log( len(x) ) )
  coeff[1:] = (pywt.threshold(i,value=uthresh,mode="soft") for i in coeff[1:])
  y = pywt.waverec(coeff,wavelet,mode="per")
  del(x)
  return y
  
from statsmodels.robust import mad
def doCWTDenoise(tm_in):
  numTraces = tm_in.traceCount
  sampleCnt = tm_in.numPoints
  traces = zeros((numTraces,sampleCnt),float32)
  data = zeros((numTraces,16),uint8)
  data_out = zeros((numTraces,16),uint8)
  savedDataIndex = 0
  CONFIG_WRITEFILE = getVariable("writefile")
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
  print("Saving...")
  support.filemanager.save(CONFIG_WRITEFILE,traces=traces[0:savedDataIndex],data=data[0:savedDataIndex],data_out=data_out[0:savedDataIndex])

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
  CONFIG_WRITEFILE = getVariable("writefile")
  for i in range(0,numTraces):
    print("Flipping IO for trace %d..." % i)
    traces[savedDataIndex,:] = tm_in.getSingleTrace(i)
    # print(unpackKeeloq(tm_in.getSingleData(i))[::-1])
    # print(packKeeloq(unpackKeeloq(tm_in.getSingleData(i))[::-1]))
    # sys.exit(0)
    data[savedDataIndex,:] = packKeeloq(unpackKeeloq(tm_in.getSingleData(i))[::-1])
    data_out[savedDataIndex,:] = packKeeloq(unpackKeeloq(tm_in.getSingleDataOut(i)[::-1])[::-1])
    savedDataIndex += 1
  print("Saving...")
  support.filemanager.save(CONFIG_WRITEFILE,traces=traces[0:savedDataIndex],data=data[0:savedDataIndex],data_out=data_out[0:savedDataIndex])

def doLowpass(tm_in):
  numTraces = tm_in.traceCount
  sampleCnt = tm_in.numPoints
  traces = zeros((numTraces,sampleCnt),float32)
  data = zeros((numTraces,16),uint8)
  data_out = zeros((numTraces,16),uint8)
  savedDataIndex = 0
  CONFIG_WRITEFILE = getVariable("writefile")
  (CONFIG_LCUTOFF,CONFIG_SAMPLERATE,CONFIG_ORDER) = getLowpass()
  for i in range(0,numTraces):
    print("Lowpassed traced %d..." % i)
    x = tm_in.getSingleTrace(i)
    r2 = butter_lowpass_filter(x,CONFIG_LCUTOFF,CONFIG_SAMPLERATE,CONFIG_ORDER)
    traces[savedDataIndex,:] = r2
    data[savedDataIndex,:] = tm_in.getSingleData(i)
    data_out[savedDataIndex,:] = tm_in.getSingleDataOut(i)
    savedDataIndex += 1
  print("Saving...")
  support.filemanager.save(CONFIG_WRITEFILE,traces=traces[0:savedDataIndex],data=data[0:savedDataIndex],data_out=data_out[0:savedDataIndex])

def doBandpass(tm_in):
  numTraces = tm_in.traceCount
  sampleCnt = tm_in.numPoints
  traces = zeros((numTraces,sampleCnt),float32)
  data = zeros((numTraces,16),uint8)
  data_out = zeros((numTraces,16),uint8)
  savedDataIndex = 0
  CONFIG_WRITEFILE = getVariable("writefile")
  (CONFIG_LCUTOFF,CONFIG_HCUTOFF,CONFIG_SAMPLERATE,CONFIG_ORDER) = getBandpass()
  for i in range(0,numTraces):
    print("Bandpassed traced %d..." % i)
    x = tm_in.getSingleTrace(i)
    r2 = butter_bandpass_filter(x,CONFIG_LCUTOFF,CONFIG_HCUTOFF,CONFIG_SAMPLERATE,CONFIG_ORDER)
    traces[savedDataIndex,:] = r2
    data[savedDataIndex,:] = tm_in.getSingleData(i)
    data_out[savedDataIndex,:] = tm_in.getSingleDataOut(i)
    savedDataIndex += 1
  print("Saving...")
  support.filemanager.save(CONFIG_WRITEFILE,traces=traces[0:savedDataIndex],data=data[0:savedDataIndex],data_out=data_out[0:savedDataIndex])

def doEarthquake(tm_in):
  numTraces = tm_in.traceCount
  sampleCnt = tm_in.numPoints
  traces = zeros((numTraces,sampleCnt),float32)
  data = zeros((numTraces,16),uint8)
  data_out = zeros((numTraces,16),uint8)
  CONFIG_WRITEFILE = getVariable("writefile")
  CONFIG_SLIDEAMOUNT = int(getOptionalVariable("slidemax",1500))
  savedDataIndex = 0
  for i in range(0,numTraces):
    x = tm_in.getSingleTrace(i)
    rval = int(-(CONFIG_SLIDEAMOUNT)) + random.randint(0,CONFIG_SLIDEAMOUNT * 2)
    print(("Index %d, rolling %d!" % (i,rval)))
    traces[savedDataIndex,:] = roll(x,rval)
    data[savedDataIndex,:] = tm_in.getSingleData(i)
    data_out[savedDataIndex,:] = tm_in.getSingleDataOut(i)
    savedDataIndex += 1
  print("Saving...")
  support.filemanager.save(CONFIG_WRITEFILE,traces=traces[0:savedDataIndex],data=data[0:savedDataIndex],data_out=data_out[0:savedDataIndex])

def doSlicer(tm_in):
  CONFIG_REFTRACE = getVariable("ref")
  CONFIG_REF_OFFSET = getVariable("ref_offset")
  CONFIG_REF_LENGTH = getVariable("ref_length")
  CONFIG_SLICE_DIST = getVariable("slicedist")
  CONFIG_WRITEFILE = getVariable("writefile")
  CONFIG_SAD_CUTOFF = getVariable("sad_cutoff")
  maxSlicesBackwards = getVariable("slices_backwards")
  maxSlicesForwards = getVariable("slices_forwards")
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
  print("Saving...")
  support.filemanager.save(CONFIG_WRITEFILE,traces=traces,data=data,data_out=data_out)

def doSAD(tm_in):
  numTraces = tm_in.traceCount
  sampleCnt = tm_in.numPoints
  traces = zeros((numTraces,sampleCnt),float32)
  data = zeros((numTraces,16),uint8)
  data_out = zeros((numTraces,16),uint8)
  CONFIG_REFTRACE = getVariable("ref")
  CONFIG_LOWPASS = getLowpass()
  CONFIG_SAD_CUTOFF = getVariable("sad_cutoff")
  CONFIG_WRITEFILE = getVariable("writefile")
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
        # traces[savedDataIndex,:] = roll(x,msi)
        data[savedDataIndex,:] = tm_in.getSingleData(i)
        data_out[savedDataIndex,:] = tm_in.getSingleDataOut(i)
        savedDataIndex += 1
    else:
      print(("Index %d, discarding (MSV is %f)" % (i,msv)))
  print("Saving...")
  support.filemanager.save(CONFIG_WRITEFILE,traces=traces[0:savedDataIndex],data=data[0:savedDataIndex],data_out=data_out[0:savedDataIndex])

def dispatchAlign(tm_in):
  global CFG_GLOBALS
  CONFIG_STRATEGY = getVariable("strategy")
  if CONFIG_STRATEGY in ("sad","SAD"):
    print("Using strategy: Align by Sum of Absolute Differences")
    doSAD(tm_in)
  elif CONFIG_STRATEGY in ("earthquake","EARTHQUAKE"):
    print("Using strategy: Misalign by time-quake! Yay for testing!")
    doEarthquake(tm_in)
  elif CONFIG_STRATEGY in ("corr","CORR"):
    print("Using strategy: Align by Maximum Correlation")
    doCORR(tm_in)
  elif CONFIG_STRATEGY in ("wavelet","WAVELET"):
    print("Using strategy: Wavelet Denoise")
    doCWTDenoise(tm_in)
  elif CONFIG_STRATEGY in ("bandpass","BANDPASS"):
    print("Using strategy: Band Pass")
    doBandpass(tm_in)
  elif CONFIG_STRATEGY in ("lowpass","LOWPASS"):
    print("Using strategy: Low Pass")
    doLowpass(tm_in)
  elif CONFIG_STRATEGY in ("keeloq","KEELOQ"):
    print("Using strategy: Flip Keeloq IO Special")
    doFlipKeeloqIO(tm_in)
  elif CONFIG_STRATEGY.upper() == "SLICER":
    print("Using strategy: SlipNSlide Slice Extractor")
    doSlicer(tm_in)
  else:
    print("Strategy must be one of SAD, CORR, CWT")
    return

def doSingleCommand(cmd,tm_in):
  tokens = cmd.split(" ")
  if tokens[0] == "set" and len(tokens) >= 2:
    tx = " ".join(tokens[1:])
    (argname,argval) = tx.split("=")
    CFG_GLOBALS[argname] = eval(argval)
  elif tokens[0] == "vars":
    for k in CFG_GLOBALS.keys():
      print("%s=%s" % (k,CFG_GLOBALS[k]))
  elif tokens[0] == "savecw":
    print("Saving as ChipWhisperer format...")
    tm_in.save_cw()
  elif tokens[0] in ["rem","#"]:
    pass
  elif tokens[0] in ["r","run"]:
    dispatchAlign(tm_in)
  elif tokens[0] in ["q","quit"]:
    print("Bye!")
    sys.exit(0)
  elif len(cmd) == 0:
    pass
  else:
    print("Unknown / invalid command")

def doCommands(CONFIG_READFILE,CONFIG_CMDFILE):
  global CFG_GLOBALS
  tm_in = support.filemanager.TraceManager(CONFIG_READFILE)
  if CONFIG_CMDFILE is not None:
    f = open(CONFIG_CMDFILE)
    cmds = [d.rstrip() for d in f.readlines()]
    for i in range(0,len(cmds)):
      doSingleCommand(cmds[i],tm_in)
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
      CFG_GLOBALS["writefile"] = opt
    elif arg in ("-c","--cmdfile"):
      CONFIG_CMDFILE = opt
  if CONFIG_READFILE is None:
    print("You must specify an input file with -f / --infile")
    sys.exit(0)
  if os.path.isfile(CONFIG_READFILE) is False:
    print("Source file %s not valid" % CONFIG_READFILE)
    sys.exit(0)
  doCommands(CONFIG_READFILE,CONFIG_CMDFILE)


