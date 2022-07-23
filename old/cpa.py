#!/usr/bin/env python3

import numpy as np
from scipy.signal import butter, lfilter, freqz
import support.resultviz
from numpy import *
import getopt
import sys
import glob
import binascii
import support.filemanager
import support.attack

TRACE_OFFSET = 0
TRACE_LENGTH = 0
TRACE_MAX = 0

CONFIG_PLOT = True
CONFIG_LEAKMODEL = "helpmsg"

leakmodel = None
resultViz = None

def deriveKey(tm,OptionManager):
  global CONFIG_LEAKMODEL
  global CONFIG_PLOT
  global TRACE_MAX
  global leakmodel
  leakmodel = support.attack.fetchModel(CONFIG_LEAKMODEL)
  if hasattr(leakmodel,"loadOptions"):
    leakmodel.loadOptions(OptionManager)
  else:
    print("LeakModel '%s' doesn't have loadOptions, ignoring" % CONFIG_LEAKMODEL)
  leakmodel.loadPlaintextArray(tm.loadPlaintexts())
  leakmodel.loadCiphertextArray(tm.loadCiphertexts())
  bestguess = [0] * leakmodel.keyLength
  meant = tm.getMeant()[TRACE_OFFSET:TRACE_OFFSET + TRACE_LENGTH]
  print(meant)
  # meant = np.mean(data,axis=0,dtype=np.float64)[TRACE_OFFSET:TRACE_OFFSET + TRACE_LENGTH] # this should be static.
  for bnum in range(0,leakmodel.keyLength):
    cpaoutput = [0]  * leakmodel.fragmentMax
    maxcpa = [0] * leakmodel.fragmentMax
    print("Correlating hypotheses for byte %d" % bnum)
    for kguess in range(0,leakmodel.fragmentMax):
      sumnum = np.zeros(TRACE_LENGTH)
      sumden1 = np.zeros(TRACE_LENGTH)
      sumden2 = np.zeros(TRACE_LENGTH)
      if TRACE_MAX == 0:
        trace_count = tm.traceCount
        # trace_count = plaintexts[:,0].size
      else:
        trace_count = TRACE_MAX
      hyp = zeros(trace_count)
      for tnum in range(0,trace_count):
        hyp[tnum] = leakmodel.genIVal(tnum,bnum,kguess) # bin(desManager[tnum].generateSbox(bnum,kguess)).count("1")
      meanh = np.mean(hyp,dtype=np.float64)
      for tnum in range(0,trace_count):
        hdiff = (hyp[tnum] - meanh)
        tdiff = tm.getSingleTrace(tnum)[TRACE_OFFSET:TRACE_OFFSET + TRACE_LENGTH] - meant
        sumnum = sumnum + (hdiff * tdiff)
        sumden1 = sumden1 + hdiff * hdiff
        sumden2 = sumden2 + tdiff * tdiff
      d_ = np.sqrt(sumden1 * sumden2)
      d = np.zeros(len(d_))
      for d_index in range(0,len(d_)):
        if d_[d_index] == 0.0:
          d[d_index] = 1.0
        else:
          d[d_index] = d_[d_index]
      cpaoutput[kguess] = sumnum / d
      maxcpa[kguess] = max(abs(cpaoutput[kguess]))
    if CONFIG_PLOT:
      global resultViz
      resultViz.addData(bnum,list(range(0,leakmodel.fragmentMax)),maxcpa)
    bestguess[bnum] = np.argmax(maxcpa)
    sortedcpa = np.argsort(maxcpa)[::-1]
    print("Selected: %02x; CPA: %f, %02x %f, %02x %f" % (bestguess[bnum], maxcpa[bestguess[bnum]], sortedcpa[1], maxcpa[sortedcpa[1]], sortedcpa[2], maxcpa[sortedcpa[2]]))
    # for tnum_cumulative in range(0,plaintexts[:,0].size):
    #   desManager[tnum_cumulative].saveCumulative(bnum,bestguess[bnum])
    #   desManager[tnum_cumulative].disableCumulative = True
  return bestguess

fn = None

def usage():
  print(" cpa.py : part of the fuckshitfuck toolkit")
  print("----------------------------------------------")
  print(" -a : specify algo + leakage model")
  print(" -h : prints this message")
  print(" -o : offset to start correlating from")
  print(" -n : number of samples per trace")
  print(" -f : trace file (.npz from grab3.py)")
  print(" --txt : do not plot (ssh mode)")

if __name__ == "__main__":
  opts, remainder = getopt.getopt(sys.argv[1:],"ha:o:n:f:c:",["algo=","help","offset=","samples=","file=","count=","txt","opt="])
  OptionManager = {}
  for opt, arg in opts:
    if opt in ("-h","--help"):
      usage()
      sys.exit(0)
    elif opt in ("-o","--offset"):
      TRACE_OFFSET = int(arg)
    elif opt in ("-n","--samples"):
      TRACE_LENGTH = int(arg)
    elif opt in ("-c","--count"):
      TRACE_MAX = int(arg)
    elif opt in ("-a","--algo"):
      CONFIG_LEAKMODEL =  arg
    elif opt == "--txt":
      CONFIG_PLOT = False
    elif opt == "--opt":
      try:
        (key,val) = arg.split(":")
        OptionManager[key.strip()] = val.strip()
      except:
        print("Fatal: could not split '%s' on ':'" % arg)
        sys.exit(0)
    elif opt in ("-f","--file"):
      fn = arg
  print("TRACE_OFFSET = %d" % TRACE_OFFSET)
  print("TRACE_LENGTH = %d" % TRACE_LENGTH)
  if fn is None:
    print("You must specify a file with -f")
    sys.exit(0)
  print("Stage 1: Loading plaintexts...")
  tm = support.filemanager.TraceManager(fn)
  # tm.mapBlocks()
  if TRACE_LENGTH == 0:
    TRACE_LENGTH = tm.numPoints
  print("Stage 2: Deriving key... wish me luck!")
  if CONFIG_PLOT:
    resultViz = support.resultviz.VisualizerApp()
  r = deriveKey(tm,OptionManager)
  out = ""
  for i in range(0,leakmodel.keyLength):
    out += "%02x " % int(r[i])
  print("Done: %s" % out)
  out = ""
  if CONFIG_PLOT:
    resultViz.render()
    resultViz.mainloop()
