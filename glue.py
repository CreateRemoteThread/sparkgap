#!/usr/bin/env python3

# todo this really needs a ui to prevent big oofs

import sys
import support.filemanager

def usage():
  print("./glue.py [infile1] [infile2] [outfile]")

def doGlue():
  if len(sys.argv) != 4:
    usage()
    sys.exit(0)
  FILE_IN_1 = sys.argv[1]
  FILE_IN_2 = sys.argv[2]
  FILE_OUT = sys.argv[3]
  tm1 = support.filemanager.TraceManager(FILE_IN_1)
  tm2 = support.filemanager.TraceManager(FILE_IN_2) 
  if tm1.numPoints != tm2.numPoints:
    print("fatal: trace sets must have equal numbers of points")
    sys.exit(0)
  bigbonk = tm1.traceCount + tm2.traceCount
  cs_out = support.filemanager.CaptureSet(tracecount = bigbonk, samplecount = tm1.numPoints, in_len = 16, out_len = 16)
  # TEXT_1 = [0xAA] * 16
  # TEXT_2 = [0x00] * 16
  for i in range(0,tm1.traceCount):
    cs_out.addTrace(tm1.traces[i],tm1.data_out[i],tm1.data_in[i])
  for i in range(0,tm2.traceCount):
    cs_out.addTrace(tm2.traces[i],tm2.data_out[i],tm2.data_in[i])
  cs_out.save(FILE_OUT)

if __name__ == "__main__":
  doGlue()
