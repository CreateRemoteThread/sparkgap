#!/usr/bin/env python3

import sys
import getopt
import sys
import uuid
import time
import random
import numpy as np
import triggerbuddy
import support.filemanager

fe = None
drv = None

def acquireInterface(interfacename):
  global fe
  try:
    exec("from frontends.%s import CaptureInterface; fe = CaptureInterface()" % interfacename,globals())
  except:
    print("Unable to acquire interface '%s'" % interfacename)
    fe = None

def acquireDriver(interfacename):
  global drv
  try:
    exec("from drivers.%s import DriverInterface; drv = DriverInterface()" % interfacename,globals())
  except:
    print("Unable to acquire driver '%s'" % interfacename)
    drv = None

def usage():
  print("capturebuddy")
  print("  -f <frontend>: set the acquisition frontend")
  print("  -d <driver>: set the logic driver")
  print("  -c <cmdfile>: run commands from file")

import uuid

config = {}
config["tracecount"] = 5
config["samplecount"] = 15000
config["writefile"] = "%s" % uuid.uuid4()

def runCaptureTask():
  global fe,drv,config
  missedCount = 0
  fe.init()
  drv.init(fe)
  traces = np.zeros((config["tracecount"],config["samplecount"]),np.float32)
  data = np.zeros((config["tracecount"],16),np.uint8)         # RAND
  data_out = np.zeros((config["tracecount"],16),np.uint8)     # AUTN
  for i in range(0,config["tracecount"]):
    print("Running job: %d/%d. %d missed" % (i,config["tracecount"],missedCount))
    (next_rand, next_autn) = drv.drive()
    time.sleep(3.0)
    dataA = fe.capture()
    if len(dataA) == 0:
      print("Missed a trace!")
      missedCount += 1
      traces[i:] = np.zeros(config["samplecount"])
    else:
      traces[i:] = dataA
    data[i:] = next_rand
    data_out[i:] = next_autn
  support.filemanager.save(config["writefile"],traces=traces,data=data,data_out=data_out)

trig = None

def processCommand(c):
  global fe, drv, trig, config
  tokens = c.split(" ")
  if cmd in ("q","quit"):
    fe.close()
    drv.close()
    print("bye!")
    sys.exit(0)
  elif tokens[0] in ("t","trig","trigger"):
    if trig is None:
      trig = triggerbuddy.TriggerBuddy()
      config["trigger"] = trig
      fe.config["trigger"] = trig
      drv.config["trigger"] = trig
    if len(tokens) == 1:
      return
    else:
      tcmd = " ".join(tokens[1:])
      trig.processCommand(tcmd)
  elif cmd in ("r","run"):
    runCaptureTask()
  elif tokens[0] == "vars":
    for i in config.keys():
      print("%s=%s" % (i,config[i]))
    for i in fe.config.keys():
      print("%s=%s" % (i,fe.config[i]))
    for i in drv.config.keys():
      print("%s=%s" % (i,drv.config[i]))
  elif tokens[0] == "set":
    cmdx = " ".join(tokens[1:])
    (varname,varval) = cmdx.split("=")
    config[varname] = eval(varval)
    fe.config[varname] = eval(varval)
    drv.config[varname] = eval(varval)
  elif tokens[0] == "fe.set":
    cmdx = " ".join(tokens[1:])
    (varname,varval) = cmdx.split("=")
    fe.config[varname] = eval(varval)
  elif tokens[0] == "drv.set":
    cmdx = " ".join(tokens[1:])
    (varname,varval) = cmdx.split("=")
    drv.config[varname] = eval(varval)
  else:
    print("Unknown command %s" % cmd)

if __name__ == "__main__":
  print("capturebuddy")
  CMDFILE = None
  optlist, args = getopt.getopt(sys.argv[1:],"hf:d:c:",["help","frontend=","driver=","cmdfile="])
  for arg,value in optlist:
    if arg in ("-h","--help"):
      usage()
      sys.exit(0)
    elif arg in ("-f","--frontend"):
      acquireInterface(value)
    elif arg in ("-d","--driver"):
      acquireDriver(value)
    elif arg in ("-c","--cmdfile"):
      CMDFILE = value
    else:
      print("Sorry, not implemented yet")
      sys.exit(0)
  if fe is None:
    print("No acquisition frontend, bye!")
    sys.exit(0)
  elif drv is None:
    print("No driver backend, bye!")
    sys.exit(0)
  if CMDFILE is not None:
    f = open(CMDFILE,"r")
    cmd_array = [d.rstrip() for d in f.readlines()]
    for c in cmd_array:
      processCommand(c)
    f.close()
  while True:
    cmd = input(" > ").lstrip().rstrip()
    processCommand(cmd)
