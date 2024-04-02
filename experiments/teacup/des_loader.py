#!/usr/bin/env python3

import getopt
import sparkgap
import sparkgap.filemanager
import sys
import rainbow
from rainbow import HammingWeight,TraceConfig
from rainbow.generics import rainbow_arm
import numpy as np
import gc
import random
import binascii

CONFIG_INFILE  = None
CONFIG_OUTFILE = None

opts, rems = getopt.getopt(sys.argv[1:],"f:w:",["--file=","--writefile="])
for arg,val in opts:
  if arg in ("-w","--writefile"):
    CONFIG_OUTFILE = val
  elif arg in ("-f","--file"):
    CONFIG_INFILE = val

if CONFIG_INFILE is None or CONFIG_OUTFILE is None:
  print("You must populate both -f and -w")
  sys.exit(0)

cs = None

KEY_ADDR = 0x18cb8
DATA_ADDR = 0x18cc0
OUT_ADDR = 0x18cb0

DODES_END = 0x8974

for i in range(0,50):
  print("Beginning attempt")
  emu = rainbow_arm(trace_config=TraceConfig(register=HammingWeight()))
  emu.load(CONFIG_INFILE)
  emu.setup()
  rand_input = np.array([random.randint(0,0xFF) for i in range(0,8)],dtype=np.uint8)
  emu[DATA_ADDR] = bytes(rand_input[0:4])
  emu[DATA_ADDR + 4] = bytes(rand_input[4:8])
  emu.start(emu.functions["doDESEncrypt"] , DODES_END)
  new_trace = np.fromiter(map(lambda event: event["register"], emu.trace),dtype=np.float32)
  rand_output = emu[OUT_ADDR:OUT_ADDR+8]
  if cs is None:
    cs = sparkgap.filemanager.CaptureSet(tracecount=50,samplecount=len(new_trace),in_len=8,out_len=8)
    cs.addTrace(new_trace,rand_input,rand_output)
  else:
    cs.addTrace(new_trace,rand_input,rand_output)
  print("Run %d, %s -> %s" % (i,binascii.hexlify(rand_input),binascii.hexlify(rand_output)))
  del(emu)
  gc.collect()

cs.save(CONFIG_OUTFILE)
