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

KEY_ADDR = 0x19e64
DATA_ADDR = 0x19e74
OUT_ADDR = 0x19e84

DOAES_END = 0x9c18

rand_key = np.array([random.randint(0,0xFF) for i in range(0,16)],dtype=np.uint8)
key_str = " ".join(["%02x" % x for x in rand_key])

if CONFIG_REKEY is False:
  print("Key is %s" % key_str)

for i in range(0,CONFIG_COUNT):
  emu = rainbow_arm(trace_config=TraceConfig(register=HammingWeight()))
  emu.load(CONFIG_INFILE)
  emu.setup()
  if CONFIG_REKEY is True:
    rand_key = np.array([random.randint(0,0xFF) for i in range(0,16)],dtype=np.uint8)
    key_str = " ".join(["%02x" % x for x in rand_key])
    print("Key is %s" % key_str)
  emu[KEY_ADDR] = bytes(rand_key[0:4])
  emu[KEY_ADDR+4] = bytes(rand_key[4:8])
  emu[KEY_ADDR+8] = bytes(rand_key[8:12])
  emu[KEY_ADDR+12] = bytes(rand_key[12:16])
  rand_input = np.array([random.randint(0,0xFF) for i in range(0,16)],dtype=np.uint8)
  emu[DATA_ADDR] = bytes(rand_input[0:4])
  emu[DATA_ADDR + 4] = bytes(rand_input[4:8])
  emu[DATA_ADDR + 8] = bytes(rand_input[8:12])
  emu[DATA_ADDR + 12] = bytes(rand_input[12:16])
  emu.start(emu.functions["doAESEncrypt"] , DOAES_END)
  new_trace = np.fromiter(map(lambda event: event["register"], emu.trace),dtype=np.float32)
  rand_output = emu[OUT_ADDR:OUT_ADDR+16]
  if cs is None:
    cs = sparkgap.filemanager.CaptureSet(tracecount=CONFIG_COUNT,samplecount=len(new_trace),in_len=16,out_len=16)
    cs.addTrace(new_trace,rand_input,rand_output)
  else:
    cs.addTrace(new_trace,rand_input,rand_output)
  print("Run %d/%d, %s -> %s" % (i,CONFIG_COUNT,binascii.hexlify(rand_input),binascii.hexlify(rand_output)))
  del(emu)
  gc.collect()

cs.save(CONFIG_OUTFILE)

if CONFIG_REKEY is False:
  print("Reminder: key is %s" % key_str)
