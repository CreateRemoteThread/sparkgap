#!/usr/bin/env python3

# Keeloq DPA.

import random
import support.attacks.support.keeloq as keeloq

def unpackKeeloq(plaintext):
  out = ""
  for i in range(0,9):
    out = format(plaintext[i],"08b") + out
  return out[6:]

def unpackKeeloqInt(plaintext):
  ival = unpackKeeloq(plaintext)
  nextstep = ival[0:32]
  return int(nextstep[::-1],2)

class AttackModel:
  def __init__(self):
    print("Loading Keeloq Attack Model")
    self.keyLength = 1
    # self.fragmentMax = 0x10
    self.fragmentMax = 0x100
    print("Creating fragCache")
    self.fragCache = {} 

  def loadPlaintextArray(self,plaintexts):
    print("Loading Keeloq Ciphertexts")
    self.kl = [unpackKeeloq(pt) for pt in plaintexts]
    self.kl_ints = [unpackKeeloqInt(pt) for pt in plaintexts]

  def loadCiphertextArray(self,ct):
    print("LoadCiphertextArray called, should be 0")
    self.ct = ct

  # Correlate via HD of 8th bit (should be *reasonably* stable?)
  def genIVal(self,tnum,bnum,kguess):
    knownKey = 0x02 # 18debd
    knownKeyLen = 8 # 32
    decr = self.kl_ints[tnum]
    if tnum in self.fragCache.keys():
      decr = self.fragCache[tnum]
    else:
      knownKeyBitString = format(knownKey,"0%db" % knownKeyLen)
      for i in range(0,len(knownKeyBitString)):
        (decr,dist1) = keeloq.keeloqDecryptKeybitHD(decr,int(knownKeyBitString[i],2))
      print("Caching intermediate decrypt for trace %d" % tnum)
      self.fragCache[tnum] = decr
    keyGuessBitString = format(kguess,"08b")
    for i in range(0,len(keyGuessBitString)):
      (decr,dist1) = keeloq.keeloqDecryptKeybitHD(decr,int(keyGuessBitString[i],2))
    return dist1

  def distinguisher(self,tnum,bnum,kguess):
    knownKey = 0x0218  # known keys get glued onto the end...
    knownKeyLen = 16
    decr = self.kl_ints[tnum]
    knownKeyBitString = format(knownKey,"0%db" % knownKeyLen)
    for i in range(0,len(knownKeyBitString)):
      (decr,dist1) = keeloq.keeloqDecryptKeybitHD(decr,int(knownKeyBitString[i],2))
    keyGuessBitString = format(kguess,"08b")
    for i in range(0,len(keyGuessBitString)):
      (decr,dist1) = keeloq.keeloqDecryptKeybitHD(decr,int(keyGuessBitString[i],2))
    return dist1 > 16
    # return decr % 2 == 0
    # return decr % 2 == 0
