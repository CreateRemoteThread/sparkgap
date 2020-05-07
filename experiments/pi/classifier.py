#!/usr/bin/env python3

import base64
import csv
import sys
import glob
import re
import support

crashes = 0
entries = 0
wins = 0

report = support.ReportingCore()

PC_crashes = {}

for fn in glob.glob("logs/*.csv"):
  with open(fn) as csvfile:
    csvreader = csv.reader(csvfile,delimiter=',')
    for row in csvreader:
      entries += 1
      (loc,len,result) = row
      result = result[2:-1]
      if result == "Li90cnltZQ0KNjI1MDAwMA0KZ3JpOjEwMDAvMTAwMC8xMDAwcGlAcmFzcGJlcnJ5cGk6fiQg":
        # default-result
        report.addResult(len,loc,status=support.Status.Expected)
        continue
      elif result == "Li90cnltZQ0K":
        report.addResult(len,loc,status=support.Status.Mute)
        continue
      else:
        report.addResult(len,loc,status=support.Status.Glitch)
        try:
          result = base64.b64decode(result).decode("utf-8")
        except:
          continue
        print(result)
        crashes += 1
        if "winner" in result:
          wins += 1
        if "PC is at" in result:
          f = re.search("PC is at (.*?)\r",result)
          pc_result = f.groups(0)[0]
          if pc_result in PC_crashes.keys():
            PC_crashes[pc_result] += 1
          else:
            PC_crashes[pc_result] = 1

print("Statistics...")
print("%d Wins" % wins)
print("%d Crashes" % crashes)
print("%d Total Entries" % entries)

d_view = [(d,v) for (v,d) in list(PC_crashes.items())]
d_view.sort(reverse=True)

for d,v in d_view:
  print("%s:%d" % (v,d))

# report.startPlot()

# for x in PC_crashes.keys():
#   print("%s:%d" % (x,PC_crashes[x]))
