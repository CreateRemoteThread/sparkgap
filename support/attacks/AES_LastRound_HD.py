#!/usr/bin/env python3

# developing this first

import chipwhisperer.analyzer as cwa
from chipwhisperer.analyzer.attacks.models.aes.funcs import inv_sbox, inv_shiftrows

def getHammingWeight(x):
  return bin(x).count("1")

print("Initializing HW LUT")
HW_LUT = [getHammingWeight(x) for x in range(0,256)]

class AttackModel:
  INVSHIFT_undo = [0,5,10,15,4,9,14,3,8,13,2,7,12,1,6,11]
  def __init__(self):
    self.keyLength = 16
    self.fragmentMax = 256

  def loadPlaintextArray(self,pt):
    print("Loading plaintext array for AES SBox Out HW Attack...")
    self.pt = pt

  def loadCiphertextArray(self,ct):
    self.ct = ct

  def genIVal(self,tnum,bnum,kguess):
    global HW_LUT
    st10 = self.ct[tnum][self.INVSHIFT_undo[bnum]]
    st9 = inv_sbox(self.ct[tnum][bnum] ^ kguess)
    return HW_LUT[st9 ^ st10]

  def distinguisher(self,tnum,bnum,kguess):
    return self.genIVal(tnum,bnum,kguess) >= 4
