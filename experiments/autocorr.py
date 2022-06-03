#!/usr/bin/env python3

# todo work out how riscure(?) did theirs

import support.filemanager
import numpy as np
import sys
import getopt
import matplotlib.pyplot as plt

CONFIG_FILE = None
CONFIG_START = None
CONFIG_NUMSAMPLES = None

if __name__ == "__main__":
  opts, args = getopt.getopt(sys.argv[1:],"f:o:n:",["file=","offset=","numsamples="])
  for opt, arg in opts:
    if opt in ["-f","--file"]:
      CONFIG_FILE = arg
    elif opt in ["-o","--offset"]:
      CONFIG_START = int(arg)
    elif opt in ["-n","--numsamples"]:
      CONFIG_NUMSAMPLES = int(arg)
  if CONFIG_FILE is None:
    print("error: you must supply a file via -f")
    sys.exit(0)

tm = support.filemanager.TraceManager(CONFIG_FILE)
d = tm.getSingleTrace(0)

if CONFIG_START is None:
  CONFIG_START = 0
if CONFIG_NUMSAMPLES is None:
  CONFIG_NUMSAMPLES = len(d)

baseSample = d[CONFIG_START:CONFIG_START + CONFIG_NUMSAMPLES]
maxCorr = 0

CONFIG_SLIDELEN = CONFIG_NUMSAMPLES * 2

corrdb = np.zeros(len(d))

for i in range(1,len(d)):
  testSample = np.roll(d,i)
  corrdb[i] = np.corrcoef(baseSample,testSample)[0,1]

plt.plot(corrdb)

print("max = %f" % max(corrdb))
print("argmax = %d" % np.argmax(corrdb))
plt.show()
