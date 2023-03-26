#!/usr/bin/env python3

import os
import sys
import getopt
import sys
import uuid
import time
import random
import numpy as np
import traceback
import readline
import datetime
import sparkgap.filemanager

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

CFG_SLEEP = 1.6

def runCaptureTask():
  global fe,drv,config
  missedCount = 0
  fe.init()
  drv.init(fe)
  LEIA_Hack = False
  if "leia_hack" in config.keys():
    print("Capture: LEIA USIM Hack Enabled")
    LEIA_Hack = True
    hack_captureSet = sparkgap.filemanager.CaptureSet(tracecount=config["tracecount"],samplecount=config["samplecount"])
  captureSet = sparkgap.filemanager.CaptureSet(tracecount=config["tracecount"],samplecount=config["samplecount"])
  # traces = np.zeros((config["tracecount"],config["samplecount"]),np.float32)
  # data = np.zeros((config["tracecount"],config["len_in"]),np.uint8)         # RAND
  # data_out = np.zeros((config["tracecount"],config["len_out"]),np.uint8)     # AUTN
  for i in range(0,config["tracecount"]):
    print("=" * 80)
    print("[%s] Running job: %d/%d. %d missed" % (datetime.datetime.now(),i,config["tracecount"],missedCount))
    print("=" * 80)
    if LEIA_Hack:
      print("Fetching extra parameter")
      (next_rand, next_autn, resp_type) = drv.drive(None)
    else:
      (next_rand, next_autn) = drv.drive(None)
    time.sleep(CFG_SLEEP)
    if next_rand is None and next_autn is None:
      dataA = []
    else:
      dataA = fe.capture()
    if len(dataA) == 0:
      print("Missed a trace!")
      missedCount += 1
    else:
      if LEIA_Hack:
        if resp_type == 2:
          hack_captureSet.addTrace(dataA,next_rand,next_autn)
        else:
          captureSet.addTrace(dataA,next_rand,next_autn)
      else:
        captureSet.addTrace(dataA,next_rand,next_autn)
  vars = {}
  if config["writefile"] is None:
    print("Writefile is unconfigured, not saving results...")
  elif config["writefile"] == "/tmp":
    tempfile = "/tmp/%s" % uuid.uuid4()
    captureSet.save(tempfile)
    # sparkgap.filemanager.save(tempfile,traces=traces,data=data,data_out=data_out)
    print("Saved to %s" % tempfile)
  else:
    if LEIA_Hack:
      wHead = hack_captureSet.writeHead
      save_traces = hack_captureSet.traces[0:wHead]
      save_data_in = hack_captureSet.data_in[0:wHead]
      save_data_out = hack_captureSet.data_out[0:wHead]
      hack_captureSet.save(config["writefile"] + ".leia_hack") # ,traces=save_traces,data=save_data_in,data_out=save_data_out)
      # sparkgap.filemanager.save(config["writefile"] + ".leia_hack",traces=leia_traces,data=leia_data,data_out=leia_data_out)
    wHead = captureSet.writeHead
    save_traces = captureSet.traces[0:wHead]
    save_data_in = captureSet.data_in[0:wHead]
    save_data_out = captureSet.data_out[0:wHead]
    captureSet.save(config["writefile"]) # ,traces=save_traces,data=save_data_in,data_out=save_data_out)
    
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
    if config["writefile"] is None and config["tracecount"] >= 50:
      print("Sanity check failed: 50+ traces and no writefile")
    else:
      runCaptureTask()
  elif tokens[0] == "vars":
    for i in config.keys():
      print("%s=%s" % (i,strfix(config[i])))
    # for i in fe.config.keys():
    #   print("%s=%s" % (i,strfix(fe.config[i])))
    # for i in drv.config.keys():
    #   print("%s=%s" % (i,strfix(drv.config[i])))
  elif tokens[0] in ["savevars","dumpvars"] and len(tokens) == 2:
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
  elif tokens[0] == "unset":
    varname = tokens[1]
    if varname in config.keys():
      del(config[varname])
      print("Deleted variable '%s'" % varname)
    else:
      print("Could not find variable '%s'" % varname)
  elif tokens[0] == "set":
    cmdx = " ".join(tokens[1:])
    try:
      (varname,varval) = cmdx.split("=")
    except:
      var_tok = cmdx.split(" ")
      varname = var_tok[0]
      varval = " ".join(var_tok[1:])
    try:
      p = eval(varval)
    except Exception as ex:
      print("Exception: could not evaluate '%s'" % varval)
      print("No variables set!")
    else:
      config[varname] = p
      if varname == "DEBUG" and p is True:
        print("DEBUG set, forcing tracecount to 1")
        config["tracecount"] = 1
  # elif tokens[0] == "fe.set":
  #   cmdx = " ".join(tokens[1:])
  #   (varname,varval) = cmdx.split("=")
  #   fe.config[varname] = eval(varval)
  # elif tokens[0] == "drv.set":
  #   cmdx = " ".join(tokens[1:])
  #   (varname,varval) = cmdx.split("=")
  #   drv.config[varname] = eval(varval)
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
  fe.config = config
  drv.config = config
  if CMDFILE is not None:
    f = open(CMDFILE,"r")
    cmd_array = [d.rstrip() for d in f.readlines()]
    for c in cmd_array:
      processCommand(c)
    f.close()
  while True:
    cmd = input(" > ").lstrip().rstrip()
    processCommand(cmd)
