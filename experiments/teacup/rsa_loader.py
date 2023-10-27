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
  print("./rsa_loader.py [elffile]")
  sys.exit(0)

cs = None

KEY_ADDR = 0x92dc
DATA_ADDR = 0x92d4

print("Generating keys...")
emu = rainbow_arm()
emu.load(sys.argv[1])
emu.setup()
emu.start(emu.functions["doGenKeys"] , 0x8050)
print("Real pubkey collected...")
real_pubkey = emu[0x18f50:0x18f50+16]
del(emu)
gc.collect()

for i in range(0,1):
  emu = rainbow_arm(trace_config=TraceConfig(register=HammingWeight()))
  emu.load(sys.argv[1])
  emu.setup()
  emu[0x18f50:0x18f50+16] = real_pubkey
  emu.start(emu.functions["doEncrypt"] , 0x8024)
  new_trace = np.fromiter(map(lambda event: event["register"], emu.trace),dtype=np.float32)
  del(emu)
  gc.collect()
  if cs is None:
    cs = sparkgap.filemanager.CaptureSet(tracecount=50,samplecount=len(new_trace),in_len=8,out_len=8)
    cs.addTrace(new_trace,rand_input,rand_output)
  else:
    cs.addTrace(new_trace,rand_input,rand_output)
  print("Run %d, %s -> %s" % (i,binascii.hexlify(rand_input),binascii.hexlify(rand_output)))
  del(emu)
  gc.collect()

cs.save("out.hdf")
