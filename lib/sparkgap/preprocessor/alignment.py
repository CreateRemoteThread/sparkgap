#!/usr/bin/env python3

import scipy.io
from scipy.signal import butter,lfilter,freqz
import numpy as np
from numpy import *

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

def getMaxCorrCoeff(trace1,trace2,varMgr):
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

def getMinimalSAD(trace1,trace2,varMgr):
  minimalSAD = varMgr.getVariable("sad_cutoff") 
  minimalSADIndex = 0
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
          # print(ms)
        except:
          print("WTF")
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
            print("WTF")
            continue
          if ms < minimalSAD:
            minimalSAD = ms
            minimalSADIndex = i
  return (minimalSADIndex,minimalSAD)

def doCORR(tm_in,varMgr):
  numTraces = tm_in.traceCount
  sampleCnt = tm_in.numPoints
  lenPT = len(tm_in.data_in[0])
  lenCT = len(tm_in.data_out[0])
  traces = zeros((numTraces,sampleCnt),float32)
  data = zeros((numTraces,lenPT),uint8)
  data_out = zeros((numTraces,lenCT),uint8)
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
    (msv,msi) = getMaxCorrCoeff(r2,ref,varMgr)
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

def doEarthquake(tm_in,varMgr):
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
  # sparkgap.filemanager.save(CONFIG_WRITEFILE,traces=traces[0:savedDataIndex],data=data[0:savedDataIndex],data_out=data_out[0:savedDataIndex])


def doSAD(tm_in,varMgr):
  numTraces = tm_in.traceCount
  sampleCnt = tm_in.numPoints
  lenPT = len(tm_in.data_in[0])
  lenCT = len(tm_in.data_out[0])
  traces = zeros((numTraces,sampleCnt),float32)
  data = zeros((numTraces,lenPT),uint8)
  data_out = zeros((numTraces,lenCT),uint8)
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
    (msi,msv) = getMinimalSAD(r2,ref,varMgr)
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
  # sparkgap.filemanager.save(CONFIG_WRITEFILE,traces=traces[0:savedDataIndex],data=data[0:savedDataIndex],data_out=data_out[0:savedDataIndex])

