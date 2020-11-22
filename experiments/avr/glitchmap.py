#!/usr/bin/env python3

import matplotlib as mpl
import sys

if __name__ == "__main__":
  for fn in sys.argv[1:]:
    print("Loading %s" % fn)
    f = open(fn)
    for l in [rx.rstrip().replace("]","] ") for rx in f.readlines()]:
      if l.startswith("E:"):
        tokens = l.split(' ')
        if tokens[-1] == "Success!":
          print(tokens[0])
    f.close()
