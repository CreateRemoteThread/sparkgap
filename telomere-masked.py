#!/usr/bin/env python3

import sys
import unicorn as uc
import capstone as cs
import rainbow
import random
from rainbow.generics import rainbow_arm
from rainbow.utils import hw
import support.filemanager
import numpy as np

TRACE = []
TRACECOUNT = 2500

cs = None
for i in range(0,TRACECOUNT):
  rand_key = np.array([random.randint(0,0xFF) for i in range(0,16)],dtype=np.uint8)
  emu = rainbow_arm(sca_mode=True)
  emu.load("experiments/ml/masked.elf")
  emu[0x20000000] = bytes(rand_key[0:4])
  emu[0x20000000 + 4] = bytes(rand_key[4:8])
  emu[0x20000000 + 8] = bytes(rand_key[8:12])
  emu[0x20000000 + 12] = bytes(rand_key[12:16])
  emu.start(emu.functions["doAES"] | 1,0x08000262)
  new_trace = np.fromiter(map(hw,emu.sca_values_trace),dtype=np.float32)
  if cs is None:  
    cs = support.filemanager.CaptureSet(tracecount=TRACECOUNT,samplecount=len(new_trace),in_len=16,out_len=16)
  cs.addTrace(new_trace,rand_key,rand_key)
  print("Emulating run %d (saved %d samples) " % (i,len(new_trace)))

cs.save("emu_masked.hdf")
