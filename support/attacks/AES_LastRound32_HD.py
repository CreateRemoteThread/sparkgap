#!/usr/bin/env python3

import chipwhisperer.analyzer as cwa
from chipwhisperer.analyzer.attacks.models.aes.funcs import inv_sbox

def getHammingWeight(x):
  return bin(x).count("1")

print("Initializing HW LUT")
HW_LUT = [getHammingWeight(x) for x in range(0,256)]

class AttackModel:
  INVSHIFT_undo = [0,5,10,15,4,9,14,3,8,13,2,7,12,1,6,11]
  def __init__(self):
    self.keyLength = 4
    self.fragmentMax = 0xFFFFFFFF

  def loadPlaintextArray(self,pt):
    print("Loading plaintext array for AES LastRound State Diff HD Attack...")
    self.pt = pt

  def loadCiphertextArray(self,ct):
    self.ct = ct

  def genIVal(self,tnum,bnum_,kguess):
    global HW_LUT
    hd_sum = 0
    for i in range(0,4):
      bnum = bnum_ * 4 + i
      byte = 3 - i
      kg = (kguess & (0xFF << (byte * 8))) >> (byte * 8)
      st10 = self.ct[tnum][self.INVSHIFT_undo[bnum]]
      st9 = inv_sbox(self.ct[tnum][bnum] ^ kg)
      hd_sum += bin(st9 ^ st10).count("1")
    return hd_sum

  def distinguisher(self,tnum,bnum,kguess):
    return self.genIVal(tnum,bnum,kguess) >= 16
