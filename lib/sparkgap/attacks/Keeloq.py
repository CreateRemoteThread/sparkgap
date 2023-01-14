#!/usr/bin/env python3

# Keeloq DPA.

import sys
import random
import sparkgap.attacks.sparkgap.keeloq as keeloq

def getHammingWeight(x):
  return bin(x).count("1")

print("Initializing HW LUT")
HW_LUT = [getHammingWeight(x) for x in range(0,256)]

# print("Performing decryption test")
# decr = keeloq.keeloqDecryptKeybit(0x11223344,1)
# print(bin(decr))
# decr = keeloq.keeloqDecryptKeybit(decr,1)
# print(bin(decr))
# decr = keeloq.keeloqDecryptKeybit(decr,1)
# print(bin(decr))
# decr = keeloq.keeloqDecryptKeybit(decr,1)
# print(bin(decr))

# print("Perfroming decryption with alternate Key2")
# decr = keeloq.keeloqDecryptKeybit(0x11223344,1)
# print(bin(decr))
# decr = keeloq.keeloqDecryptKeybit(decr,0)
# print(bin(decr))
# decr = keeloq.keeloqDecryptKeybit(decr,1)
# print(bin(decr))
# decr = keeloq.keeloqDecryptKeybit(decr,1)
# print(bin(decr))
# sys.exit(0)

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
