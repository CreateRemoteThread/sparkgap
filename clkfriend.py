#!/usr/bin/env python3

import getopt
import sys
import re

def usage():
  print("./clkfriend.py v0.1")
  print("  --from: [20Hz]")
  print("  --to: [ms]")

clkRegex = re.compile("(\d+)(\w+)")

if __name__ == "__main__":
  if len(sys.argv) == 1:
    usage()
    sys.exit(0)
  opts, args = getopt.getopt(sys.argv[1:], "f:t:", ["--from=", "--to="])
  for (opt, val) in opts:
    if opt in ["-f","--from"]:
      CLK_FROM = val
    elif opt in ["-t", "--to"]:
      CLK_TO = val
    elif opt in ["-c", "--clk"]:
      CLK_TARG = val


