#!/usr/bin/env python3

import sys
import support.filemanager
import binascii
import getopt

if __name__ == "__main__":
  print("./peek.py")

tm = support.filemanager.TraceManager(sys.argv[1])

tc = len(tm.traces)
for i in range(0,min(10,tc)):
  di = tm.getSingleData(i)
  do = tm.getSingleDataOut(i)
  print("%s:%s" % (binascii.hexlify(di),binascii.hexlify(do)))

