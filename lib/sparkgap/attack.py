#!/usr/bin/env python3

import sys
import glob
import os
import importlib.machinery
import importlib.util

if "SPARKGAP_MDLDIR" in os.environ.keys():
  ENV_MDLDIR = os.environ["SPARKGAP_MDLDIR"]
else:
  ENV_MDLDIR = "models"

CFG_KNOWNATTACKS = ["AES_LastRound_HD","AES_LastRound_HW","AES_SboxOutMasked_HW","AES_SboxOut_HD","AES_SboxOut_HW","AES_SboxOut_LSB","AES_TTableOut_HW","DES_SboxOut_HW","Keeloq","XorOut_HD","XorOut_HW"]
# ['attacks/__init__.py', 'attacks/AES_SboxOut_HW.py', 'attacks/DES_SboxOut_HW.py', 'attacks/AES_TTableOut_HW.py', 'attacks/XorOut_HW.py']
def usage():
  global CFG_KNOWNATTACKS
  print("Attack model must be one of:")
  for a in CFG_KNOWNATTACKS:
    print(" - %s" % a)
  fl = glob.glob("%s/*.py" % ENV_MDLDIR) # imported from ../
  for f in fl:
    fx = f.replace("%s/" % ENV_MDLDIR,"")
    fx2 = fx.replace(".py","")
    if fx2 == "__init__":
      continue
    print(" - %s" % fx2)

def fetchModel(modelname):
  if "." in modelname:
    print("Loading external module from path '%s'" % modelname)
    if not os.path.isfile(modelname):
      print("Fatal: '%s' isn't a file")
      sys.exit(0)
    loader = importlib.machinery.SourceFileLoader( "extmodule" , modelname)
    spec = importlib.util.spec_from_loader("extmodule",loader)
    fe = importlib.util.module_from_spec(spec)
    loader.exec_module(fe)
    print("Loading OK, instantiating AttackModel()...")
    am = fe.AttackModel()
    print("Loading OK, returning AttackModel")
    return am
  print("Loading internal module from name '%s'" % modelname)
  try:
    if modelname in CFG_KNOWNATTACKS:
      f = importlib.import_module("sparkgap.attacks.%s" % (modelname))
    else:
      f = importlib.import_module("%s.%s" % (ENV_MDLDIR,modelname))
    return f.AttackModel()
  except Exception as ex:
    print(ex)
    print("Could not load attack model '%s'" % modelname)
    usage()
    sys.exit(0)

if __name__ == "__main__":
  print("ATTACK MODEL LOADER, DO NOT CALL DIRECTLY.")
