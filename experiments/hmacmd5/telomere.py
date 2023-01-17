#!/usr/bin/env python3

import getopt
import sys
import unicorn as uc
import capstone as cs
import rainbow
import random
from rainbow.generics import rainbow_arm
from rainbow.utils import hw
import sparkgap.filemanager
import numpy as np
import gc

TRACE = []
TRACECOUNT = 15
WRITEFILE = "emu_normal.hdf"

random.seed()

rekey = False

if len(sys.argv) >= 1:
  opts,remainder = getopt.getopt(sys.argv[1:],"rc:w:",["rekey","count=","writefile="])
  for opt, arg in opts:
    if opt in ("-r","--rekey"):
      rekey = True
    elif opt in ("-c","--count"):
      TRACECOUNT = int(arg)
    elif opt in ("-w","--writefile"):
      WRITEFILE = arg

import binascii
import hashlib

rand_key = np.array([random.randint(0,0xFF) for i in range(0,16)],dtype=np.uint8)
cs = None
for i in range(0,TRACECOUNT):
  emu = rainbow_arm(sca_mode=True)
  emu.load("nucleo_f030_target.elf")
  rand_text = np.array([random.randint(0,0xFF) for i in range(0,16)],dtype=np.uint8)
  # emu[0x20000000] = bytes(rand_text[0:4])
  # emu[0x20000000 + 4] = bytes(rand_text[4:8])
  # emu[0x20000000 + 8] = bytes(rand_text[8:12])
  # emu[0x20000000 + 12] = bytes(rand_text[12:16])
  hash_in = b"\x00" * 64
  # hash_in = emu[0x20000000] + emu[0x20000000 + 4] + emu[0x20000000 + 8] + emu[0x20000000 + 12]
  emu.start(emu.functions["do_test_MD5"] | 1,0x0800053C)
  new_trace = np.fromiter(map(hw,emu.sca_values_trace),dtype=np.float32)
  hash_out = emu[0x20000028] + emu[0x20000028+4] + emu[0x20000028+8] + emu[0x20000028+12]
  print("".join(["%02x" % x for x in hash_out]))
  print("Expected: %s" % hashlib.md5(hash_in).hexdigest())
  if cs is None: 
    print("Creating CaptureSet")
    samplecount = len(new_trace)
    cs = sparkgap.filemanager.CaptureSet(tracecount=TRACECOUNT,samplecount=len(new_trace),in_len=16,out_len=16)
    cs.addTrace(new_trace,rand_text,rand_key)
  else:
    if len(new_trace) != samplecount:
      print("Skipping run %d (tracelen %d)" % (i,len(new_trace)))
      continue
    cs.addTrace(new_trace,rand_text,rand_key)
  print("Emulating run %d (saved %d samples) " % (i,len(new_trace)))
  del(emu)
  gc.collect()
if rekey is False:
  print(rand_key)

cs.save(WRITEFILE)