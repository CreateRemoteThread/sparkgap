#!/usr/bin/env python3

import numpy
import getopt
import sys

def usage():
  print("todo: usage")

if __name__ == "__main__":
  if len(sys.argv) == 1:
    usage()
    sys.exit(0)
  opts, args = getopt.getopt(sys.argv[1:],"f:t:",["from=","to="])
  for arg, val in opts:
    if arg in ["-f","--from"]:
      FROM_VAL = val
    elif arg in ["-t","--to"]:
      TO_VAL = val
 
