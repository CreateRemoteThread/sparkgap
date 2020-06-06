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
    self.fragmentMax = 0b10000

  def loadPlaintextArray(self,plaintexts):
    print("Loading Keeloq Ciphertexts")
    self.kl = [unpackKeeloq(pt) for pt in plaintexts]
    self.kl_ints = [unpackKeeloqInt(pt) for pt in plaintexts]

  def loadCiphertextArray(self,ct):
    print("LoadCiphertextArray called, should be 0")
    self.ct = ct

  def genIVal(self,tnum,bnum,kguess):
    print("Keeloq IVal Calculation: Returning 0")
    return 0
    # eturn bin(self.desManager[tnum].generateSbox(bnum,kguess)).count("1")

  # FOUR ROUNDS _ONLY_
  def distinguisher(self,tnum,bnum,kguess):
    f = format(kguess,"04b")
    (decr,dist) = keeloq.keeloqDecryptKeybitHD(self.kl_ints[tnum],int(f[3],2))
    (decr,dist) = keeloq.keeloqDecryptKeybitHD(decr,int(f[2],2))
    (decr,dist) = keeloq.keeloqDecryptKeybitHD(decr,int(f[1],2))
    (decr,dist) = keeloq.keeloqDecryptKeybitHD(decr,int(f[0],2))
    return dist > 16
