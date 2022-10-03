#!/usr/bin/env python3

import sys
import matplotlib.pyplot as plt

data = open(sys.argv[1],"r")
l = [l_.rstrip() for l_ in data.readlines()]
data.close()
times_crashed = []
times_normal = []
times_fault = []
for line in l:
  if "GREPTHIS" in line:
    delay_time = line.split("]")[0][1:]
    if "except" in line:
      times_crashed.append(float(delay_time))
    elif "Permission denied" in line:
      times_normal.append(float(delay_time))
    else:
      times_fault.append(float(delay_time))
  else:
    continue

plt.scatter(times_normal,[0 for l in times_normal])
plt.scatter(times_crashed,[1 for l in times_crashed])
plt.scatter(times_fault,[2 for l in times_fault])
plt.show()
