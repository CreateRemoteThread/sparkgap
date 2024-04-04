#!/usr/bin/env python3

# XTEA needs two rounds to attack
# try1 yields KEY0 ???1 ???2 KEY3
# try2 yields ???0 KEY1 KEY2 ???3

import numpy as np
import math

class AttackModel:
  def __init__(self):
    self.keyLength = 2
    self.fragmentMax = 0x100000000
    self.HW_LUT = [bin(x).count("1") for x in range(0,0x100)]

  def loadPlaintextArray(self,plaintexts):
    print("Loading plaintext array for XTEA HW Attack")
    self.pt = plaintexts
    print("[Preprocessing] creating v0 and v1 arrays...")
    self.v0 = np.zeros(len(self.pt),np.uint32)
    self.v1 = np.zeros(len(self.pt),np.uint32)
    self.intval_left = np.zeros(len(self.pt),np.uint32)
    self.intval_right = np.zeros(len(self.pt),np.uint32)
    for tnum in range(0,len(self.pt)):
      v0 = self.pt[tnum][0] + self.pt[tnum][1] * 0x100 + self.pt[tnum][2] * 0x10000 + self.pt[tnum][3] * 0x1000000
      v1 = self.pt[tnum][4] + self.pt[tnum][5] * 0x100 + self.pt[tnum][6] * 0x10000 + self.pt[tnum][7] * 0x1000000
      self.v0[tnum] = ((v1 << 4 ^ v1 >> 5) + v1)
      self.v1[tnum] = ((v0 << 4 ^ v0 >> 5) + v0)
    print("[Preprocessing] v0 and v1 arrays done")

  def loadCiphertextArray(self,ct):
    print("Loading plaintext array for XTEA HW Attack")
    self.ct = ct

  def genIVal(self,tnum,bnum,kguess):
    if bnum == 0:
      return bin(self.v0[tnum] ^ kguess).count("1")
    else:
      return bin(self.v1[tnum] ^ kguess).count("1")

  def genIValRaw(self,tnum,bnum,kguess):
    if bnum == 0:
      return self.v0[tnum] ^ kguess
    else:
      return self.v1[tnum] ^ kguess

  def distinguisher(self,tnum,bnum,kguess):
    return self.genIValRaw(tnum,bnum,kguess) % 2 == 0

if __name__ == "__main__":
  print("This is a test file for external loading of attack models")
