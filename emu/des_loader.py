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
CONFIG_REKEY = False
CONFIG_COUNT = 250

opts, rems = getopt.getopt(sys.argv[1:],"f:w:kc:",["--file=","--writefile=","--rekey","--count="])
for arg,val in opts:
  if arg in ("-w","--writefile"):
    CONFIG_OUTFILE = val
  elif arg in ("-f","--file"):
    CONFIG_INFILE = val
  elif arg in ("-k","--rekey"):
    CONFIG_REKEY = True
  elif arg in ("-c","--count"):
    CONFIG_COUNT = int(val)

if CONFIG_INFILE is None or CONFIG_OUTFILE is None:
  print("You must populate both -f and -w")
  sys.exit(0)

cs = None

KEY_ADDR = 0x18ce8
DATA_ADDR = 0x18cd8
OUT_ADDR = 0x18ce0

DODES_START = 0x8954
DODES_END = 0x8974   # WHOLE

rand_key = np.array([0x11,0x22,0x33,0x44,0x55,0x66,0x77,0x88])
key_str = " ".join(["%02x" % x for x in rand_key])

if CONFIG_REKEY is False:
  print("Key is %s" % key_str)

for i in range(0,CONFIG_COUNT):
  emu = rainbow_arm(trace_config=TraceConfig(register=HammingWeight()))
  emu.load(CONFIG_INFILE)
  emu.setup()
  if CONFIG_REKEY is True:
    rand_key = np.array([random.randint(0,0xFF) for i in range(0,8)],dtype=np.uint8)
    key_str = " ".join(["%02x" % x for x in rand_key])
    print("Key is %s" % key_str)
  rand_input = np.array([random.randint(0,0xFF) for i in range(0,8)],dtype=np.uint8)
  emu[DATA_ADDR] = bytes(rand_input[0:4])
  emu[DATA_ADDR+4] = bytes(rand_input[4:8])
  emu.start(DODES_START , DODES_END)
  new_trace = np.fromiter(map(lambda event: event["register"], emu.trace),dtype=np.float32)
  out_output = emu[OUT_ADDR:OUT_ADDR+8]
  if cs is None:
    cs = sparkgap.filemanager.CaptureSet(tracecount=CONFIG_COUNT,samplecount=len(new_trace),in_len=8,out_len=8)
    cs.addTrace(new_trace,rand_input,out_output)
  else:
    cs.addTrace(new_trace,rand_input,out_output)
  print("Run %d/%d, %s -> %s" % (i,CONFIG_COUNT,binascii.hexlify(rand_input),binascii.hexlify(out_output)))
  del(emu)
  gc.collect()

if CONFIG_OUTFILE != "q":
  cs.save(CONFIG_OUTFILE)

if CONFIG_REKEY is False:
  print("Reminder: key is %s" % key_str)
