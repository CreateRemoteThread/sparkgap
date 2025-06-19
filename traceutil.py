#!/usr/bin/env python3

import sys
import getopt
import readline
import sparkgap.filemanager

def doGlue(cfg):
  tm1 = sparkgap.filemanager.TraceManager(cfg["infile1"])
  tm2 = sparkgap.filemanager.TraceManager(cfg["infile2"])
  CFG_LABEL1 = None
  CFG_LABEL2 = None
  if "label1" in cfg.keys():
    CFG_LABEL1 = cfg["label1"]
    print("Loading tag 1 of %d" % CFG_LABEL1)
  if "label2" in cfg.keys():
    CFG_LABEL2 = cfg["label2"]
    print("Loading tag 2 of %d" % CFG_LABEL2)
  if tm1.numPoints != tm2.numPoints:
    print("fatal: trace sets must have equal numbers of points")
    return
  if len(tm1.data_in[0]) != len(tm2.data_in[0]):
    print("fatal: trace set data_in must be equal in length")
    return
  if CFG_LABEL1 is None and CFG_LABEL2 is None:
    if len(tm1.data_out[0]) != len(tm2.data_out[0]):
      print("fatal: trace set data_out must be equal in length")
      return
  if (CFG_LABEL1 is None and CFG_LABEL2 is not None) or (CFG_LABEL1 is not None and CFG_LABEL2 is None):
    print("fatal / fixme: either label both sets or label only one")
    return
  bigbonk = tm1.traceCount + tm2.traceCount
  cs_out = sparkgap.filemanager.CaptureSet(tracecount=bigbonk,samplecount=tm1.numPoints,in_len = len(tm1.data_in[0]),out_len = len(tm1.data_out[0]))
  for i in range(0,tm1.traceCount):
    if CFG_LABEL1 is None:
      cs_out.addTrace(tm1.traces[i],[int(CFG_LABEL1)] * 8,[int(CFG_LABEL1)] * 8) 
    else:
      cs_out.addTrace(tm1.traces[i],tm1.data_in[i],tm1.data_out[i])
  for i in range(0,tm2.traceCount):
    if CFG_LABEL2 is None:
      cs_out.addTrace(tm1.traces[i],[int(CFG_LABEL2)] * 8,[int(CFG_LABEL2)] * 8) 
    else:    
      cs_out.addTrace(tm2.traces[i],tm2.data_in[i],tm2.data_out[i]) 
  cs_out.save(cfg["writefile"])
  print("glue operation complete")

import binascii

def doPeek(cfg):
  tm = sparkgap.filemanager.TraceManager(cfg["infile1"])
  tc = len(tm.traces)
  for i in range(0,min(10,tc)):
    di = tm.getSingleData(i)
    do = tm.getSingleDataOut(i)
    print("%s:%s" % (binascii.hexlify(di),binascii.hexlify(do)))

dispatch = {}
dispatch["glue"] = (doGlue,["infile1","infile2","writefile"])
dispatch["peek"] = (doPeek,["infile1"])
config = {}

print(" >> traceutil.py")

while True:
  cmd = input(" > ").rstrip()
  cmdTokens = cmd.split()
  if cmdTokens[0] == "set":
    cmdx = " ".join(cmdTokens[1:])
    try:
      (varname,varval) = cmdx.split("=")
    except:
      var_tok = cmdx.split(" ")
      varname = var_tok[0]
      varval = " ".join(var_tok[1:])
    try:
      p = eval(varval)
    except Exception as ex:
      print("Exception: could not evaluate '%s'" % varval)
      print("No variables set!")
    else:
      config[varname] = p
  elif cmdTokens[0] == "unset":
    if cmdTokens[1] in config.keys():
      del(config[cmdTokens[1]])
      print("Unset '%s'" % cmdTokens[1])
    else:
      print("Could not find variable '%s'" % cmdTokens[1])
  elif cmdTokens[0] in ("q","quit"):
    sys.exit(0)
  else:
    if cmdTokens[0] in dispatch.keys():
      (fn,reqs) = dispatch[cmdTokens[0]]
      enableCall = True
      for r in reqs:
        if r not in config.keys():
          print("Required parameter '%s' missing" % r)
          enableCall = False
      if enableCall is True:
        print("Dispatching '%s'" % cmdTokens[0])
        fn(config)
    else:
      print("Unknown command '%s'" % cmdTokens[0])
