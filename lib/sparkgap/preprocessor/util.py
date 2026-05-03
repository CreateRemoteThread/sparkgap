#!/usr/bin/env python3

import os
import sparkgap.filemanager

def doGlue(tm_in,varMgr):
  print("doGlue: traceset join utility")
  infile1 = os.path.expanduser(varMgr.getVariable("infile1",prompt=True))
  infile2 = os.path.expanduser(varMgr.getVariable("infile2",prompt=True))
  tm1 = sparkgap.filemanager.TraceManager(infile1)
  tm2 = sparkgap.filemanager.TraceManager(infile2)
  print("doGlue: traceset1 %s" % infile1)
  print("doGlue: traceset2 %s" % infile2)
  if tm1.numPoints != tm2.numPoints:
    print("doGlue: traceset1 has %d points, traceset2 has %d points, stop" % (tm1.numPoints, tm2.numPoints))
    return
  if len(tm1.data_in[0]) != len(tm2.data_in[0]):
    print("doGlue: traceset1 data_in length unequal to traceset2 data_in length, stop")
    return
  if len(tm1.data_out[0]) != len(tm2.data_out[0]):
    print("doGlue: traceset1 data_out length unequal to traceset2 data_out length, stop") 
    return
  bigbonk = tm1.traceCount + tm2.traceCount
  cs_out = sparkgap.filemanager.CaptureSet(tracecount=bigbonk,samplecount=tm1.numPoints,in_len = len(tm1.data_in[0]),out_len = len(tm1.data_out[0]))
  for i in range(0,tm1.traceCount):
    cs_out.addTrace(tm1.traces[i],tm1.data_in[i],tm1.data_out[i])
  for i in range(0,tm2.traceCount):
    cs_out.addTrace(tm2.traces[i],tm2.data_in[i],tm2.data_out[i])
  print("doGlue: traces glued, returning")
  return (cs_out.traces, cs_out.data_in, cs_out.data_out)
    
   
