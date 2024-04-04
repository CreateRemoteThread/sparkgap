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
CONFIG_COUNT = 250

opts, rems = getopt.getopt(sys.argv[1:],"f:w:c:",["--file=","--writefile=","--count="])
for arg,val in opts:
  if arg in ("-w","--writefile"):
    CONFIG_OUTFILE = val
  elif arg in ("-f","--file"):
    CONFIG_INFILE = val
  elif arg in ("-c","--count"):
    CONFIG_COUNT = int(val)

if CONFIG_INFILE is None or CONFIG_OUTFILE is None:
  print("You must populate both -f and -w")
  sys.exit(0)

cs = None

KEY_ADDR = 0x18904
DATA_ADDR = 0x188fc
OUT_ADDR = 0x18d64

DOXTEA_END = 0x84c4

rand_input = np.array([random.randint(0,0xFF) for i in range(0,8)],dtype=np.uint8)
key_str = " ".join(["%02x" % p for p in rand_input])

print("Key is %s" % key_str)

for i in range(0,CONFIG_COUNT):
  emu = rainbow_arm(trace_config=TraceConfig(register=HammingWeight()))
  emu.load(CONFIG_INFILE)
  emu.setup()
  emu[KEY_ADDR] = bytes(rand_input[0:4])
  emu[KEY_ADDR+4] = bytes(rand_input[4:8])
  rand_input = np.array([random.randint(0,0xFF) for i in range(0,8)],dtype=np.uint8)
  emu[DATA_ADDR] = bytes(rand_input[0:4])
  emu[DATA_ADDR + 4] = bytes(rand_input[4:8])
  emu.start(emu.functions["doXTEA"] , DOXTEA_END)
  new_trace = np.fromiter(map(lambda event: event["register"], emu.trace),dtype=np.float32)
  rand_output = emu[OUT_ADDR:OUT_ADDR+8]
  if cs is None:
    cs = sparkgap.filemanager.CaptureSet(tracecount=CONFIG_COUNT,samplecount=len(new_trace),in_len=8,out_len=8)
    cs.addTrace(new_trace,rand_input,rand_output)
  else:
    cs.addTrace(new_trace,rand_input,rand_output)
  print("Run %d, %s -> %s" % (i,binascii.hexlify(rand_input),binascii.hexlify(rand_output)))
  del(emu)
  gc.collect()

cs.save(CONFIG_OUTFILE)
print("Reminder: Key is %s" % key_str)
