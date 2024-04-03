#!/usr/bin/env python3

# Keeloq DPA.

import sys
import random

HW8Bit = [0, 1, 1, 2, 1, 2, 2, 3, 1, 2, 2, 3, 2, 3, 3, 4, 1, 2, 2, 3, 2, 3, 3,
          4, 2, 3, 3, 4, 3, 4, 4, 5, 1, 2, 2, 3, 2, 3, 3, 4, 2, 3, 3, 4, 3, 4,
          4, 5, 2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6, 1, 2, 2, 3, 2,
          3, 3, 4, 2, 3, 3, 4, 3, 4, 4, 5, 2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5,
          4, 5, 5, 6, 2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6, 3, 4, 4,
          5, 4, 5, 5, 6, 4, 5, 5, 6, 5, 6, 6, 7, 1, 2, 2, 3, 2, 3, 3, 4, 2, 3,
          3, 4, 3, 4, 4, 5, 2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6, 2,
          3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6, 3, 4, 4, 5, 4, 5, 5, 6,
          4, 5, 5, 6, 5, 6, 6, 7, 2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5,
          6, 3, 4, 4, 5, 4, 5, 5, 6, 4, 5, 5, 6, 5, 6, 6, 7, 3, 4, 4, 5, 4, 5,
          5, 6, 4, 5, 5, 6, 5, 6, 6, 7, 4, 5, 5, 6, 5, 6, 6, 7, 5, 6, 6, 7, 6,
          7, 7, 8]

def keeloqGetHW(var):
    hw = 0
    while var > 0:
        hw = hw + HW8Bit[var % 256]
        var = var >> 8
    return hw

def keeloqGetHD(var1, var2):
    return keeloqGetHW(var1 ^ var2)

def keeloqNLF(a, b, c, d, e):
    return (d + e + a*c + a*e + b*c + b*e + c*d + d*e + a*d*e + a*c*e + a*b*d + a*b*c) % 2;

def keeloqDecryptCalcLSB(data, keybit):
    nlf = keeloqNLF((data>>30)%2, (data>>25)%2, (data>>19)%2, (data>>8)%2, (data>>0)%2)
    lsb = (keybit ^ (data>>31) ^ (data>>15) ^ nlf) % 2
    return lsb

def keeloqDecryptKeybit(data, keybit):
    return ((data & 0x7FFFFFFF)<<1) ^ keeloqDecryptCalcLSB(data, keybit)

def keeloqDecryptKeybitHD(data, keybit):
    decrypt = keeloqDecryptKeybit(data, keybit)
    return decrypt, keeloqGetHD(data, decrypt)


def getHammingWeight(x):
  return bin(x).count("1")

print("Initializing HW LUT")
HW_LUT = [getHammingWeight(x) for x in range(0,256)]

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
    knownKey = 0x112277885566
    knownKeyLen = 48
    useKnownKey = True
    # knownKey = 0x0218de # 0x0218debf # orig is 0x0218debd
    # knownKeyLen = 24 # 32
    # useKnownKey = False
    decr = self.kl_ints[tnum]
    if tnum in self.fragCache.keys():
      decr = self.fragCache[tnum]
    else:
      knownKeyBitString = format(knownKey,"0%db" % knownKeyLen)
      if useKnownKey:
        for i in range(0,len(knownKeyBitString)):
          (decr,dist1) = keeloq.keeloqDecryptKeybitHD(decr,int(knownKeyBitString[i],2))
        print("Caching intermediate decrypt for trace %d" % tnum)
        self.fragCache[tnum] = decr
    keyGuessBitString = format(kguess,"08b")
    for i in range(0,len(keyGuessBitString)):
      (decr,dist1) = keeloq.keeloqDecryptKeybitHD(decr,int(keyGuessBitString[i],2))
    return dist1

  def distinguisher(self,tnum,bnum,kguess):
    global HW_LUT
    knownKey = 0x0218de  # known keys get glued onto the end...
    knownKeyLen = 24
    useKnownKey = False
    decr = self.kl_ints[tnum]
    # return (decr >> 31) % 2 == 0
    knownKeyBitString = format(knownKey,"0%db" % knownKeyLen)
    if useKnownKey:
      for i in range(0,len(knownKeyBitString)):
        (decr,dist1) = keeloq.keeloqDecryptKeybitHD(decr,int(knownKeyBitString[i],2))
    keyGuessBitString = format(kguess,"08b")
    for i in range(0,len(keyGuessBitString)):
      (decr,dist1) = keeloq.keeloqDecryptKeybitHD(decr,int(keyGuessBitString[i],2))
    # just get the key bits we want
    mask = HW_LUT[(decr >> 24) & 0xFF]
    # print(mask > 4)
    return mask > 4
