#!/usr/bin/env python3

# Keeloq DPA.

class AttackModel:
  def __init__(self):
    print("Loading Keeloq Attack Model")
    self.keyLength = 32
    self.fragmentMax = 2

  def loadPlaintextArray(self,plaintexts):
    print("Loading Keeloq Ciphertexts (actually plaintexts lol")
    self.pt = plaintexts
    self.desManager = {}
    trace_count = plaintexts[:,0].size
    print("Pre-scheduling %d keys, this might take a while..." % trace_count)
    for tnum in range(0,trace_count):
      self.desManager[tnum] = dessupport.desIntermediateValue()
      self.desManager[tnum].preprocess(plaintexts[tnum])

  def loadCiphertextArray(self,ct):
    self.ct = ct

  def genIVal(self,tnum,bnum,kguess):
    return bin(self.desManager[tnum].generateSbox(bnum,kguess)).count("1")

  def genIValRaw(self,tnum,bnum,kguess):
    return self.desManager[tnum].generateSbox(bnum,kguess)

  def distinguisher(self,tnum,bnum,kguess):
    return self.genIValRaw(tnum,bnum,kguess) % 2 == 0
