#!/usr/bin/env python3

class AttackModel:
  def __init__(self):
    self.keyLength = 8
    self.fragmentMax = 65 # 6 bits per fragment, so absmax is 65

  def loadPlaintextArray(self,pt):
    print("Loading plaintext array for DES Xor Out HW Attack...")
    print("REMINDER: the output is key fragments, recombine them")
    self.pt = pt

  def loadCiphertextArray(self,ct):
    self.ct = ct

  def genIVal(self,tnum,bnum,kguess):
    return bin(self.pt[tnum,bnum]  ^ kguess).count("1")

  def genIValRaw(self,tnum,bnum,kguess):
    return self.pt[tnum,bnum]  ^ kguess

  def distinguisher(self,tnum,bnum,kguess):
    if bin(self.genIValRaw(tnum,bnum,kguess)).count("1") >= 4:
      return True
    else:
      return False
