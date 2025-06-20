#!/usr/bin/env python3

from numpy import *
import sparkgap.filemanager

def complex2Float(tm_in,varMgr):
  numTraces = tm_in.traceCount
  sampleCnt = (tm_in.numPoints // 2) + 1
  traces_i = zeros((numTraces,sampleCnt),float32)
  traces_q = zeros((numTraces,sampleCnt),float32)
  data = zeros((numTraces,16),uint8)
  data_out = zeros((numTraces,16),uint8)
  print("complex2float - deinterleave")
  savedDataIndex = 0
  CONFIG_WRITEFILE = varMgr.getVariable("writefile")
  for i in range(0,numTraces):
    print("Deinterleaving trace %d..." % i)
    x = tm_in.getSingleTrace(i)
    traces_i[savedDataIndex,0:len(x) // 2 - 1] = [x[i * 2] for i in range(len(x) // 2 - 1)]
    traces_q[savedDataIndex,0:len(x) // 2 - 1] = [x[i * 2 + 1] for i in range(len(x) // 2 - 1)]
    data[savedDataIndex,:] = tm_in.getSingleData(i)
    data_out[savedDataIndex,:] = tm_in.getSingleDataOut(i)
    savedDataIndex += 1
  WRITEFILE_I = CONFIG_WRITEFILE.replace(".hdf","_i.hdf")
  WRITEFILE_Q = CONFIG_WRITEFILE.replace(".hdf","_q.hdf")
  s = sparkgap.filemanager.CaptureSet(migrateData  = True)
  s.tracecount = numTraces
  s.writeHead = s.tracecount
  s.traces   = traces_i
  s.data_in  = tm_in.data_in
  s.data_out = tm_in.data_out
  print("Saving in-phase data to %s" % WRITEFILE_I)
  s.save(WRITEFILE_I)
  s.traces   = traces_q
  print("Saving out-of-phase data to %s" % WRITEFILE_Q)
  s.save(WRITEFILE_Q)
  print("Returning in-phase data, commit if you want")
  return (traces_i[0:savedDataIndex],data[0:savedDataIndex],data_out[0:savedDataIndex])  
