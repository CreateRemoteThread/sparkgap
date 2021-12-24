#!/usr/bin/env python3

from scipy.signal import butter,lfilter,freqz
from numpy import *
from scipy.fft import fft,fftfreq
import numpy as np

def butter_lowpass(cutoff, fs, order=5):
  nyq = 0.5 * fs
  normal_cutoff = cutoff / nyq
  b, a = butter(order, normal_cutoff, btype='low', analog=False)
  return b, a

def butter_lowpass_filter(data, cutoff, fs, order=5):
  b, a = butter_lowpass(cutoff, fs, order=order)
  y = lfilter(b, a, data)
  return y

def get_windowed_fft(sig,wsize=128):
  yf = np.abs(fft(sig))
  return [sum(yf[i:i+wsize]) for i in range(0,len(yf),wsize)]

def flatten_fft(sig_,fftWindow=1024):
  wHdr = fftWindow // 2
  wLast = len(sig_)
  sig = butter_lowpass_filter(sig_,150000,1800000,1)
  out = []
  while wHdr <= (wLast - fftWindow // 2):
    chunk = sig[wHdr - (fftWindow // 2):wHdr + (fftWindow // 2)]
    yf = get_windowed_fft(chunk)
    out += yf
    wHdr += fftWindow // 2
  return out
