#!/usr/bin/env python3

import cherrypicker
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
TRACECOUNT = 1500
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

rand_key = np.array([random.randint(0,0xFF) for i in range(0,16)],dtype=np.uint8)
cs = None
for i in range(0,TRACECOUNT):
  emu = rainbow_arm(sca_mode=True)
  emu.load("masked.elf")
  rand_text = np.array([random.randint(0,0xFF) for i in range(0,16)],dtype=np.uint8)
  emu[0x20000000] = bytes(rand_text[0:4])
  emu[0x20000000 + 4] = bytes(rand_text[4:8])
  emu[0x20000000 + 8] = bytes(rand_text[8:12])
  emu[0x20000000 + 12] = bytes(rand_text[12:16])
  if rekey:
    (pt,keybyte) = cherrypicker.getRandomPair()
    rand_key = np.array([random.randint(0,0xFF) for i in range(0,16)],dtype=np.uint8)
    rand_key[0] = keybyte
    rand_text[0] = pt
    emu[0x20000000] = bytes(rand_text[0:4])
    print("Rekeying : %s" % ("".join(["%02x" % x for x in rand_key])))
  emu[0x20000010] = bytes(rand_key[0:4])
  emu[0x20000010 + 4] = bytes(rand_key[4:8])
  emu[0x20000010 + 8] = bytes(rand_key[8:12])
  emu[0x20000010 + 12] = bytes(rand_key[12:16])
  print("stop1")
  emu.start(emu.functions["doAES"] | 1,0x08000262)
  print("stop2")
  new_trace = np.fromiter(map(hw,emu.sca_values_trace),dtype=np.float32)
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
