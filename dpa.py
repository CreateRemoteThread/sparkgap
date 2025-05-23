#!/usr/bin/env python3

import numpy as np
from numpy import *
import sys
import sparkgap.resultviz
import glob
import getopt
import matplotlib.pyplot as plt
import binascii
import sparkgap.filemanager
import sparkgap.attack

TRACE_OFFSET = 0
TRACE_LENGTH = None
TRACE_MAX = 0

CONFIG_PLOT = True
CONFIG_LEAKMODEL = "helpmsg"

def getUsefulTraceLength(fn):
  f = open(fn)
  c = 0
  for l_ in f.readlines():
    (data,size) = l_.rstrip().split(",")
    if np.float32(size) > 0.5:
      c += 1
    else:
      break
  f.close()
  return c


leakmodel = None
resultViz = None

def deriveKey(tm):
  global CONFIG_LEAKMODEL
  global CONFIG_PLOT
  global TRACE_MAX
  global leakmodel
  leakmodel = sparkgap.attack.fetchModel(CONFIG_LEAKMODEL)
  leakmodel.loadPlaintextArray(tm.loadPlaintexts()) 
  leakmodel.loadCiphertextArray(tm.loadCiphertexts())
  tm.cutTraces(TRACE_OFFSET,TRACE_OFFSET + TRACE_LENGTH)
  recovered = zeros(leakmodel.keyLength)
  for BYTE_POSN in range(0,leakmodel.keyLength):
    print("Attempting recovery of byte %d..." % BYTE_POSN)
    if(leakmodel.fragmentMax < 3):
      print("fragmentMax in the attack model must be >= 3 for this to work")
      sys.exit(0)
    plfh = zeros(leakmodel.fragmentMax)
    for KEY_GUESS in range(0,leakmodel.fragmentMax):
      numGroup1 = 0
      numGroup2 = 0
      group1 = zeros(TRACE_LENGTH)
      group2 = zeros(TRACE_LENGTH)
      diffProfile = zeros(TRACE_LENGTH)
      if TRACE_MAX == 0:
        trace_count = tm.traceCount
      else:
        trace_count = TRACE_MAX
      for TRACE_NUM in range(0,trace_count):
        # hypothesis = leakmodel.genIValRaw(TRACE_NUM,BYTE_POSN,KEY_GUESS) # sbox[plaintexts[TRACE_NUM,BYTE_POSN] ^ KEY_GUESS]
        if leakmodel.distinguisher(TRACE_NUM,BYTE_POSN,KEY_GUESS): #if bin(hypothesis)[2:][-1] == "1":
          group1[:] += tm.getSingleTrace(TRACE_NUM)
          numGroup1 += 1
        else:
          group2[:] += tm.getSingleTrace(TRACE_NUM)
          numGroup2 += 1
      group1[:] /= numGroup1
      group2[:] /= numGroup2
      diffProfile = abs(group1[:] - group2[:])
      plfh[KEY_GUESS] = max(diffProfile)
    sorted_dpa = argsort(plfh)[::-1]
    print("Selected %02x, %f, %02x %f, %02x %f" % (argmax(plfh),plfh[sorted_dpa[0]],sorted_dpa[1],plfh[sorted_dpa[1]],sorted_dpa[2],plfh[sorted_dpa[2]]))
    if CONFIG_PLOT:
      global resultViz
      resultViz.addData(BYTE_POSN,list(range(0,leakmodel.fragmentMax)),plfh)
      # try:
      #   # plt.plot(list(range(0,leakmodel.fragmentMax)),plfh)
      # except:
      #   print("Fault in plt.plot. CONFIG_PLOT = False")
      #  CONFIG_PLOT = False
    recovered[BYTE_POSN] = argmax(plfh)
  return recovered

fn = None

def usage():
  print(" dpa.py : part of the fuckshitfuck toolkit")
  print("----------------------------------------------")
  print(" -h : prints this message")
  print(" -o : offset to start correlating from")
  print(" -n : number of samples per trace")
  print(" -f : trace file (.npz from grab3.py)")
  print(" -a : specify algo + leakage model")
  print(" --txt : do not plot (ssh mode)")

if __name__ == "__main__":
  opts, remainder = getopt.getopt(sys.argv[1:],"ho:n:f:c:a:",["help","offset=","samples=","file=","count=","algo=","txt"])
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
    elif opt in ("-f","--file"):
      fn = arg
    elif opt in ("-a","--algo"):
      CONFIG_LEAKMODEL = arg
    elif opt == "--txt":
      CONFIG_PLOT = False
  print("TRACE_OFFSET = %d" % TRACE_OFFSET)
  if TRACE_LENGTH is None:
    print("Delayed loading TRACE_LENGTH")
  else:
    print("TRACE_LENGTH = %d" % TRACE_LENGTH)
  if fn is None:
    print("You must specify a file with -f")
    sys.exit(0)
  print("Stage 1: Loading plaintexts...")
  tm = sparkgap.filemanager.TraceManager(fn)
  TRACE_LENGTH = len(tm.traces[0]) - TRACE_OFFSET
  print("TRACE_LENGTH = %d" % TRACE_LENGTH)
  print("Deriving key... wish me luck!")
  if CONFIG_PLOT:
    resultViz = sparkgap.resultviz.VisualizerApp()
    # plt.title("%s Power Leakage v Hypothesis Overview" % CONFIG_LEAKMODEL)
    # plt.ylabel("Maximum Diff. of Means")
    # plt.xlabel("Key Hypothesis")
    # plt.show()
  r = deriveKey(tm)
  out = ""
  for i in range(0,leakmodel.keyLength):
    out += "%02x " % int(r[i])
  print("Done: %s" % out)
  out = ""
  if hasattr(leakmodel,"postprocess"):
    leakmodel.postprocess(r)
  if CONFIG_PLOT:
    resultViz.render()
    resultViz.mainloop()
