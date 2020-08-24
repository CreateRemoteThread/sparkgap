#!/usr/bin/env python3

import csv
import base64
import glob

for fn in glob.glob("logs/*.csv"):
  with open(fn) as csvfile:
    csvreader = csv.reader(csvfile,delimiter=',')
    for row in csvreader:
      (loc,len,result) = row
      result = result[2:-1]
      r = base64.b64decode(result)
      if b'ns_capable' in r:
        print(loc,len)

