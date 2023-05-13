#!/usr/bin/env python3

import sys
import glob
import os
import importlib.machinery
import importlib.util

# ['attacks/__init__.py', 'attacks/AES_SboxOut_HW.py', 'attacks/DES_SboxOut_HW.py', 'attacks/AES_TTableOut_HW.py', 'attacks/XorOut_HW.py']
def usage():
  print("Attack model must be one of:")
  fl = glob.glob("support/attacks/*.py") # imported from ../
  for f in fl:
    fx = f.replace("support/attacks/","")
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
    exec("from sparkgap.attacks.%s import AttackModel; fe = AttackModel()" % modelname,globals())
    return fe
  except Exception as ex:
    print(ex)
    print("Could not load attack model '%s'" % modelname)
    usage()
    sys.exit(0)

if __name__ == "__main__":
  print("ATTACK MODEL LOADER, DO NOT CALL DIRECTLY.")
