#!/usr/bin/env python3

import sparkgap
import sparkgap.filemanager
import sys
import rainbow
from rainbow.generics import rainbow_arm
from rainbow.utils import hw
import numpy as np
import gc
import random
import binascii

if len(sys.argv) != 2:
  print("./emu_loader.py [elffile]")
  sys.exit(0)

cs = None

KEY_ADDR = 0x18904
DATA_ADDR = 0x188fc

for i in range(0,50):
  # print("Emulating run %d..." % i)
  emu = rainbow_arm(sca_mode=True)
  emu.load(sys.argv[1])
  rand_input = np.array([random.randint(0,0xFF) for i in range(0,8)],dtype=np.uint8)
  emu[DATA_ADDR] = bytes(rand_input[0:4])
  emu[DATA_ADDR + 4] = bytes(rand_input[4:8])
  emu.start(emu.functions["doXTEA"] , 0x84c8)
  new_trace = np.fromiter(map(hw, emu.sca_values_trace),dtype=np.float32)
  rand_output = emu[0x18d64:0x18d64+8]
  if cs is None:
    cs = sparkgap.filemanager.CaptureSet(tracecount=50,samplecount=len(new_trace),in_len=8,out_len=8)
    cs.addTrace(new_trace,rand_input,rand_output)
  else:
    cs.addTrace(new_trace,rand_input,rand_output)
  print("Run %d, %s -> %s" % (i,binascii.hexlify(rand_input),binascii.hexlify(rand_output)))
  del(emu)
  gc.collect()

cs.save("out.hdf")
