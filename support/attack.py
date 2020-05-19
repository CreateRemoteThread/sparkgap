#!/usr/bin/env python3

import sys
import glob

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
  try:
    exec("from support.attacks.%s import AttackModel; fe = AttackModel()" % modelname,globals())
    return fe
  except:
    print("Could not load attack model '%s'" % modelname)
    usage()
    sys.exit(0)

if __name__ == "__main__":
  print("ATTACK MODEL LOADER, DO NOT CALL DIRECTLY.")
