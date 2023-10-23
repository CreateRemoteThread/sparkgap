#!/usr/bin/env python3

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

if len(sys.argv) != 2:
  print("./emu_loader.py [elffile]")
  sys.exit(0)

cs = None

KEY_ADDR = 0x92dc
DATA_ADDR = 0x92d4

for i in range(0,50):
  emu = rainbow_arm(trace_config=TraceConfig(register=HammingWeight()))
  emu.load(sys.argv[1])
  emu.setup()
  rand_input = np.array([random.randint(0,0xFF) for i in range(0,8)],dtype=np.uint8)
  emu[DATA_ADDR] = bytes(rand_input[0:4])
  emu[DATA_ADDR + 4] = bytes(rand_input[4:8])
  emu.start(emu.functions["doXTEA"] , 0x82a8)
  new_trace = np.fromiter(map(lambda event: event["register"], emu.trace),dtype=np.float32)
  rand_output = emu[0x92ec:0x92ec+8]
  if cs is None:
    cs = sparkgap.filemanager.CaptureSet(tracecount=50,samplecount=len(new_trace),in_len=8,out_len=8)
    cs.addTrace(new_trace,rand_input,rand_output)
  else:
    cs.addTrace(new_trace,rand_input,rand_output)
  print("Run %d, %s -> %s" % (i,binascii.hexlify(rand_input),binascii.hexlify(rand_output)))
  del(emu)
  gc.collect()

cs.save("out.hdf")
