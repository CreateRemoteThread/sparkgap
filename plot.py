#!/usr/bin/env python3

# Extremely simple signal plotting tool

import sys
import binascii
import random
from scipy.signal import butter,lfilter,freqz
import scipy.signal
from numpy import *
import time
import getopt
import matplotlib as mpl
import support.filemanager

TRIGGERS = 0

lastTime = 0.0
lastX = 0

def onclick(event):
  global lastTime, lastX
  t = time.time()
  if t - lastTime < 0.200:
    print("debounce - nope")
    return
  elif event.xdata is None:
    print("skip - event.xdata (click on graph) is none")
    return
  else:
    lastTime = t
    if lastX == 0:
      lastX = int(event.xdata)
      print("MARK: %d" % lastX)
    else:
      localX = int(event.xdata)
      fromX = min(lastX,localX)
      toX = max(lastX,localX)
      dist = toX - fromX
      print("FROM %d TO %d DIST %d" % (fromX,toX,dist))
      lastX = localX


def butter_bandpass(lowcut,highcut,fs,order=5):
  nyq = 0.5 * fs
  low = lowcut / nyq
  high = highcut / nyq
  b,a = butter(order, [low, high], btype = 'band')
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

def getTraceConfig(r_str):
  r = []
  if "," in r_str:
    tokens = r_str.split(",")
    print(tokens)
  else:
    tokens = [r_str]
  for t in tokens:
    if "-" in t:
      (t1,t2) = t.split("-")
      r += list(range(int(t1),int(t2)))
    else:
      r += [int(t)]
  return r

OFFSET = 0
COUNT = 0
RULER = []
# NUM_TRACES = 1
TRACES = []
GAIN_FACTOR =  31622.0
ADDITIONAL_FILES = []

BANDPASS_LOWCUT=1000000
BANDPASS_HIGHCUT=5000000
BANDPASS_SR = 249999999
BANDPASS_ORDER=1
BANDPASS_EN = False

LOWPASS_CUTOFF = 10000
LOWPASS_SR = 40000000
LOWPASS_ORDER = 5
LOWPASS_EN = False

FFT_BASEFREQ = 40000000
FFT_EN = False

SPECGRAM_EN = False
SPECGRAM_SR = 0

PLOT_SHOWN = False # dirty hack

TITLE = "Single Trace Plot"
XAXIS = "Sample Count"
YAXIS = "Power"

def configure_fft(arg):
  global FFT_BASEFREQ,FFT_EN,TITLE,XAXIS
  FFT_BASEFREQ = float(arg)
  TITLE = "FFT Plot (%d Hz Sample Rate)" % FFT_BASEFREQ
  XAXIS = "Frequency"
  FFT_EN = True

def configure_specgram(arg):
  global SPECGRAM_EN, TITLE, XAXIS, YAXIS, SPECGRAM_SR
  TITLE = "Spectogram View"
  SPECGRAM_EN = True
  SPECGRAM_SR = float(arg)

def configure_lowpass(in_str):
  global LOWPASS_CUTOFF, LOWPASS_SR, LOWPASS_ORDER, LOWPASS_EN, TITLE
  try:
    (cutoff,samplerate,order) = in_str.split(",")
  except:
    print("syntax: -l 10000,40000000,5 (cutoff, samplerate, order)")
    sys.exit(0)
  LOWPASS_CUTOFF = float(cutoff)
  LOWPASS_SR = float(samplerate)
  LOWPASS_ORDER = int(order)
  LOWPASS_EN = True
  TITLE = "Low Pass (%d Hz SR, %d Hz Cutoff)" % (LOWPASS_SR,LOWPASS_CUTOFF)

def configure_bandpass(in_str):
  global BANDPASS_LOWCUT, BANDPASS_HIGHCUT,BANDPASS_ORDER, BANDPASS_SR, BANDPASS_EN, TITLE
  try:
    (lowcut,highcut,samplerate,order) = in_str.split(",")
  except:
    print("syntax -b (lowcut,highcut,sr,order)")
    sys.exit(0)
  BANDPASS_LOWCUT = float(lowcut)
  BANDPASS_HIGHCUT = float(highcut)
  BANDPASS_SR = float(samplerate)
  BANDPASS_ORDER = int(order)
  BANDPASS_EN = True
  TITLE = "Band pass (%d Hz to %d Hz, %d SR)" % (BANDPASS_LOWCUT,BANDPASS_HIGHCUT,BANDPASS_SR)

def usage():
  print(" plot.py : part of the fuckshitfuck toolkit")
  print("----------------------------------------------")
  print(" -h : prints this message")
  print(" -o : offset to start plotting samples from")
  print(" -n : number of samples from offset to plot")
  print(" -c : select traces")
  print(" -f : input npz file (can be multiple)")
  print(" -r : print vertical ruler at point (NOT IMPLEMENTED)")
  print(" -l [cutoff,samplerate,order] : lowpass mode - units in hz")
  print(" -b [lowcut,highcut,samplerate,order] : bandpass mode - units in hz")
  print(" -F [samplerate] : plot fft, base freq in hz")
  print(" -s [samplerate] : plot spectrogram")
  print(" -w [filename] : write output to file. suppresses window.")

mpl.rcParams['agg.path.chunksize'] = 10000 
CONFIG_WRITEFILE = None
SPECIAL_TEST = False

if __name__ == "__main__":
  opts, remainder = getopt.getopt(sys.argv[1:],"tb:s:hl:n:o:c:r:f:F:w:",["spectrogram=","help","lowpass=","samples=","offset=","count=","ruler=","file=","fft=","highlight=","bandpass=","test"])
  for opt,arg in opts:
    if opt in ("-h","--help"):
      usage()
      sys.exit(0)
    elif opt in ("-s","--spectrogram"):
      configure_specgram(arg)
    elif opt in ("-o","--offset"):
      OFFSET = int(float(arg))
    elif opt in ("-n","--samples"):
      COUNT = int(float(arg))
    elif opt in ("-c","--count"):
      TRACES = getTraceConfig(arg)
    elif opt in ("-f","--file"):
      ADDITIONAL_FILES.append(arg)
    elif opt in ("-l","--lowpass"):
      configure_lowpass(arg)
    elif opt in ("-b","--bandpass"):
      configure_bandpass(arg)
    elif opt in ("-t","--test"):
      print("SPECIAL TEST MODE")
      SPECIAL_TEST = True
    elif opt in ("-F","--fft"):
      configure_fft(arg)
    elif opt in ("-w"):
      CONFIG_WRITEFILE = arg
    elif opt in ("-r","--ruler"):
      RULER.append(int(float(arg)))
    else:
      print("Unknown argument: %s" % opt)
      sys.exit(0) 
  if CONFIG_WRITEFILE is not None:
    mpl.use("Agg")
  if LOWPASS_EN and BANDPASS_EN:
    print("You can't have both lowpass and bandpass filters (yet!)")
    sys.exit(0)
  import matplotlib.pyplot as plt
  if [FFT_EN, LOWPASS_EN, SPECGRAM_EN, BANDPASS_EN].count(True) > 1:
    print("You can only select one of -F (FFT), -l (LOWPASS) or -b (BANDPASS)")
    sys.exit(0)
  if SPECGRAM_EN == False:
    fig, ax1 = plt.subplots()
  if len(ADDITIONAL_FILES) != 1:
    print("TraceManager no longer supports multiple files by design. Try something else")
    sys.exit(0)
  for f in ADDITIONAL_FILES:
    tm = support.filemanager.TraceManager(f)
    for i in TRACES:
      if OFFSET == 0 and COUNT == 0:
        d = tm.getSingleTrace(i)
      else:
        d = tm.getSingleTrace(i)[OFFSET:OFFSET+COUNT]
      if LOWPASS_EN: # this code is disgusting but fuck you
        d = tm.getSingleTrace(i)
        # d = df['traces'][i]
        if OFFSET == 0 and COUNT == 0:
          if SPECIAL_TEST:
            lowpassed_d = butter_lowpass_filter(d,LOWPASS_CUTOFF,LOWPASS_SR,LOWPASS_ORDER)
            std_dev = std(lowpassed_d)
            avg_dev = average(lowpassed_d)
            # peaks,_ = scipy.signal.find_peaks(lowpassed_d,prominence=[0,0.5],rel_height=0.9)
            plt.plot(lowpassed_d)
            # plt.plot(peaks,lowpassed_d[peaks],"x")
          else:
            plt.plot(butter_lowpass_filter(d,LOWPASS_CUTOFF,LOWPASS_SR,LOWPASS_ORDER))
        else:
          plt.plot(butter_lowpass_filter(d,LOWPASS_CUTOFF,LOWPASS_SR,LOWPASS_ORDER)[OFFSET:OFFSET+COUNT])
      elif BANDPASS_EN:
        d = tm.getSingleTrace(i)
        # d = df['traces'][i]
        if OFFSET == 0 and COUNT == 0:
          plt.plot(butter_bandpass_filter(d,BANDPASS_LOWCUT,BANDPASS_HIGHCUT,BANDPASS_SR,BANDPASS_ORDER))
        else:
          plt.plot(butter_bandpass_filter(d,BANDPASS_LOWCUT,BANDPASS_HIGHCUT,BANDPASS_SR,BANDPASS_ORDER)[OFFSET:OFFSET+COUNT])
      elif FFT_EN:
        n = len(d)
        k = arange(n)
        T = n / FFT_BASEFREQ
        frq = k / T
        frq = frq[list(range(n/2))]
        Y = fft.fft(d)/n
        Y = Y[list(range(n/2))]
        plt.plot(frq,abs(Y),'r') 
      elif SPECGRAM_EN:
        fig, (ax1, ax2) = plt.subplots(nrows=2)
        ax1.set_title("Power Trace")
        ax1.set_ylabel("Power")
        ax1.set_xlabel("Sample Count")
        ax1.plot(d)
        ax2.set_title("Spectogram")
        ax2.set_ylabel("Frequency Component")
        ax2.set_xlabel("Time")
        ax2.specgram(d,NFFT=1024,Fs=SPECGRAM_SR,noverlap=900)
        fig.canvas.set_window_title("plot.py")
        if CONFIG_WRITEFILE is not None:
          print("Saving to %s..." % CONFIG_WRITEFILE)
          plt.savefig(CONFIG_WRITEFILE)
        else:
          plt.show()
      else:
        print(d[0:50])
        plt.plot(d)
  if PLOT_SHOWN is False:
    plt.title(TITLE)
    plt.ylabel(YAXIS)
    plt.xlabel(XAXIS)
    plt.grid()
    fig.canvas.set_window_title("plot.py")
    if CONFIG_WRITEFILE is not None:
      print("Saving to %s..." % CONFIG_WRITEFILE)
      plt.savefig(CONFIG_WRITEFILE)
    else:
      fig.canvas.mpl_connect("button_press_event",onclick)
      plt.show()
