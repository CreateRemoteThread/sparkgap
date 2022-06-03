#!/usr/bin/env python3

from numpy import *
import numpy as np
from statsmodels.robust import mad
import scipy.io
from scipy.signal import butter,lfilter,freqz
import pywt

######################### UTILITY FUNCTIONS #########################
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


########################### ACTUAL FILTERS BELOW #####################

def doLowpass(tm_in,varMgr):
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

def doBandpass(tm_in,varMgr):
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


def doCWTDenoise(tm_in,varMgr):
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


