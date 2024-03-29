#!/usr/bin/env python3

import base64
import csv
import sys
import glob
import re
import sparkgap
import getopt

crashes = 0
entries = 0
wins = 0

report = sparkgap.ReportingCore()

PC_crashes = {}

savedCrashes = {}

report.configureLocRange(400,1000)

for fn in glob.glob("logs/*.csv"):
  with open(fn) as csvfile:
    csvreader = csv.reader(csvfile,delimiter=',')
    for row in csvreader:
      entries += 1
      (loc,len,result) = row
      loc = float(loc)
      len = float(len)
      result = result[2:-1]
      if result == "Li90cnltZQ0KNjI1MDAwMA0KZ3JpOjEwMDAvMTAwMC8xMDAwcGlAcmFzcGJlcnJ5cGk6fiQg":
        # default-result
        report.addResult(loc,len,status=sparkgap.Status.Expected)
        continue
      elif result == "Li90cnltZQ0K":
        report.addResult(loc,len,status=sparkgap.Status.Mute)
        continue
      else:
        try:
          result = base64.b64decode(result).decode("utf-8")
        except:
          result = ""
          continue
        crashes += 1
        if "winner" in result:
          wins += 1
        if "PC is at" in result:
          f = re.search("PC is at (.*?)\r",result)
          pc_result = f.groups(0)[0]
          if "commit_creds" in pc_result:
            report.addResult(loc,len,status=sparkgap.Status.Glitch)
          else:
            report.addResult(loc,len,status=sparkgap.Status.Mute)
          if pc_result in PC_crashes.keys():
            PC_crashes[pc_result] += 1
            savedCrashes[pc_result].append( (loc,len) )
          else:
            PC_crashes[pc_result] = 1
            savedCrashes[pc_result] = [ (loc,len) ]

print("Statistics...")
print("%d Wins" % wins)
print("%d Crashes" % crashes)
print("%d Total Entries" % entries)

d_view = [(d,v) for (v,d) in list(PC_crashes.items())]
d_view.sort(reverse=True)

for d,v in d_view:
  print("%s:%d" % (v,d))
  print(savedCrashes[v])

report.startPlot()

