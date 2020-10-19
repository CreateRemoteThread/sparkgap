#!/usr/bin/env python3

def getTraceConfig(r_str):
  r = []
  if "," in r_str:
    tokens = r_str.split(",")
  else:
    tokens = [r_str]
  for t in tokens:
    if "-" in t:
      (t1,t2) = t.split("-")
      r += list(range(int(t1),int(t2)))
    else:
      r += [int(t)]
  return r

