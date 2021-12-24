#!/usr/bin/env python3

from scipy.fft import fft,fftfreq
import numpy as np

def get_windowed_fft(sig,wsize=128):
  yf = np.abs(fft(sig))
  return [sum(yf[i:i+wsize]) for i in range(0,len(yf),wsize)]

def flatten_fft(sig,fftWindow=1024):
  wHdr = fftWindow // 2
  wLast = len(sig)
  out = []
  while wHdr <= (wLast - fftWindow // 2):
    chunk = sig[wHdr - (fftWindow // 2):wHdr + (fftWindow // 2)]
    yf = get_windowed_fft(chunk)
    out += yf
    # print(len(out))
    wHdr += fftWindow // 2
  return out
