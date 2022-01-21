#!/usr/bin/env python3

import os
import sys
import getopt
import sys
import uuid
import time
import random
import numpy as np
import triggerbuddy
import traceback
import readline
import datetime
import support.filemanager

fe = None
drv = None

def acquireInterface(interfacename):
  global fe
  try:
    exec("from frontends.%s import CaptureInterface; fe = CaptureInterface()" % interfacename,globals())
  except:
    print("Unable to acquire interface '%s'" % interfacename)
    print("-----------------------------------")
    traceback.print_exc()
    fe = None

def acquireDriver(interfacename):
  global drv
  try:
    exec("from drivers.%s import DriverInterface; drv = DriverInterface()" % interfacename,globals())
  except:
    print("Unable to acquire driver '%s'" % interfacename)
    print("-----------------------------------")
    traceback.print_exc()
    drv = None

def usage():
  print("capturebuddy")
  print("  -f <frontend>: set the acquisition frontend")
  print("  -d <driver>: set the logic driver")
  print("  -c <cmdfile>: run commands from file")

import uuid

config = {}
config["tracecount"] = 1
config["samplecount"] = 15000
config["len_in"] = 16
config["len_out"] = 16
config["writefile"] = None
config["tlva"] = None

def runCaptureTask():
  global fe,drv,config
  missedCount = 0
  fe.init()
  drv.init(fe)
  traces = np.zeros((config["tracecount"],config["samplecount"]),np.float32)
  data = np.zeros((config["tracecount"],config["len_in"]),np.uint8)         # RAND
  data_out = np.zeros((config["tracecount"],config["len_out"]),np.uint8)     # AUTN
  for i in range(0,config["tracecount"]):
    print("=" * 80)
    print("[%s] Running job: %d/%d. %d missed" % (datetime.datetime.now(),i,config["tracecount"],missedCount))
    print("=" * 80)
    if config["tlva"] is None:
      (next_rand, next_autn) = drv.drive(None)
    else:
      if random.randint(0,100) % 2 == 0:
        (next_rand, next_autn) = drv.drive([0xAA] * 16)
      else:
        (next_rand, next_autn) = drv.drive(None)
    time.sleep(3.0)
    if next_rand is None and next_autn is None:
      dataA = []
    else:
      dataA = fe.capture()
    if len(dataA) == 0:
      print("Missed a trace!")
      missedCount += 1
      traces[i:] = np.zeros(config["samplecount"])
      data[i:] = [0] * 16
      data_out[i:] = [0] * 16
    else:
      traces[i:] = dataA
      data[i:] = next_rand
      data_out[i:] = next_autn
  vars = {}
  if config["writefile"] is None:
    print("Writefile is unconfigured, not saving results...")
  elif config["writefile"] == "/tmp":
    tempfile = "/tmp/%s" % uuid.uuid4()
    support.filemanager.save(tempfile,traces=traces,data=data,data_out=data_out)
    print("Saved to %s" % tempfile)
  else:
    support.filemanager.save(config["writefile"],traces=traces,data=data,data_out=data_out)
    
trig = None

def strfix(var):
  if isinstance(var,str):
    return "\"%s\"" % var
  else:
    return var

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
    if config["writefile"] is not None:
      if "~" in config["writefile"]:
        print("Sanity check failed: no path expansions allowed in writefile")
        return
      try:
        f = open(config["writefile"],"w")
      except Exception as ex:
        print("Sanity check failed: %s is not writeable" % config["writefile"])
        return
      else:
        f.close()
        os.unlink(config["writefile"])
    runCaptureTask()
  elif tokens[0] == "vars":
    for i in config.keys():
      print("%s=%s" % (i,strfix(config[i])))
    for i in fe.config.keys():
      print("%s=%s" % (i,strfix(fe.config[i])))
    for i in drv.config.keys():
      print("%s=%s" % (i,strfix(drv.config[i])))
  elif tokens[0] == "savevars" and len(tokens) == 2:
    print("Saving config to %s" % tokens[1])
    f = open(tokens[1],"w")
    for i in config.keys():
      f.write("c:%s=%s\n" % (i,strfix(config[i])))
    for i in fe.config.keys():
      f.write("f:%s=%s\n" % (i,strfix(fe.config[i])))
    for i in drv.config.keys():
      f.write("d:%s=%s\n" % (i,strfix(drv.config[i])))
    f.close()
  elif tokens[0] == "loadvars" and len(tokens) == 2:
    print("Loading config from %s" % tokens[1])
    f = open(tokens[1],"r")
    for x in f.readlines():
      (var,arg) = x[2:].rstrip().split("=")
      if x[0] == 'c':
        config[var] = eval(arg)
      elif x[0] == 'f':
        fe.config[var] = eval(arg)
      elif x[0] == 'd':
        drv.config[var] = eval(arg)
      # print("%c,%s,%s" % (x[0],var,arg))
    f.close()
  elif tokens[0] == "set":
    cmdx = " ".join(tokens[1:])
    (varname,varval) = cmdx.split("=")
    try:
      p = eval(varval)
    except Exception as ex:
      print("Exception: could not evaluate '%s'" % varval)
      print("No variables set!")
    else:
      config[varname] = p
      fe.config[varname] = p
      drv.config[varname] = p
      if varname == "DEBUG" and p is True:
        print("DEBUG set, forcing tracecount to 1")
        config["tracecount"] = 1
        fe.config["tracecount"] = 1
        drv.config["tracecount] = 1
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
