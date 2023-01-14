#!/usr/bin/env python3

import sys
import math
import matplotlib.pyplot as plt
import numpy as np
from Crypto.Cipher import DES
import binascii

KEY = "\x2b\x7e\x15\x16\x28\xae\xd2\xa6"
# PT  = "\xff\xff\xff\xff\xff\xff\xff\xff"
PT  = "\xa2" * 8

KEY_EXP = "".join([bin(ord(x))[2:].rjust(8,"0") for x in KEY])
PT_EXP = "".join([bin(ord(x))[2:].rjust(8,"0") for x in PT])

PC1TAB = [56, 48, 40, 32, 24, 16,  8, 0, 57, 49, 41, 33, 25, 17, 9,  1, 58, 50, 42, 34, 26, 18, 10,  2, 59, 51, 43, 35, 62, 54, 46, 38, 30, 22, 14, 6, 61, 53, 45, 37, 29, 21, 13,  5, 60, 52, 44, 36, 28, 20, 12,  4, 27, 19, 11, 3]
PC2TAB = [13, 16, 10, 23,  0,  4, 2, 27, 14,  5, 20,  9, 22, 18, 11,  3, 25,  7, 15,  6, 26, 19, 12,  1, 40, 51, 30, 36, 46, 54, 29, 39, 50, 44, 32, 47, 43, 48, 38, 55, 33, 52, 45, 41, 49, 35, 28, 31]
IPTAB = [57, 49, 41, 33, 25, 17, 9,  1, 59, 51, 43, 35, 27, 19, 11, 3, 61, 53, 45, 37, 29, 21, 13, 5, 63, 55, 47, 39, 31, 23, 15, 7, 56, 48, 40, 32, 24, 16, 8,  0, 58, 50, 42, 34, 26, 18, 10, 2, 60, 52, 44, 36, 28, 20, 12, 4, 62, 54, 46, 38, 30, 22, 14, 6]
ETAB = [ 31,  0,  1,  2,  3,  4, 3,  4,  5,  6,  7,  8, 7,  8,  9, 10, 11, 12,11, 12, 13, 14, 15, 16,15, 16, 17, 18, 19, 20,19, 20, 21, 22, 23, 24,23, 24, 25, 26, 27, 28, 27, 28, 29, 30, 31,  0]

SBOX = [
  0xE4, 0xD1, 0x2F, 0xB8, 0x3A, 0x6C, 0x59, 0x07,
  0x0F, 0x74, 0xE2, 0xD1, 0xA6, 0xCB, 0x95, 0x38,
  0x41, 0xE8, 0xD6, 0x2B, 0xFC, 0x97, 0x3A, 0x50,
  0xFC, 0x82, 0x49, 0x17, 0x5B, 0x3E, 0xA0, 0x6D,
  0xF1, 0x8E, 0x6B, 0x34, 0x97, 0x2D, 0xC0, 0x5A,
  0x3D, 0x47, 0xF2, 0x8E, 0xC0, 0x1A, 0x69, 0xB5,
  0x0E, 0x7B, 0xA4, 0xD1, 0x58, 0xC6, 0x93, 0x2F,
  0xD8, 0xA1, 0x3F, 0x42, 0xB6, 0x7C, 0x05, 0xE9,
  0xA0, 0x9E, 0x63, 0xF5, 0x1D, 0xC7, 0xB4, 0x28,
  0xD7, 0x09, 0x34, 0x6A, 0x28, 0x5E, 0xCB, 0xF1,
  0xD6, 0x49, 0x8F, 0x30, 0xB1, 0x2C, 0x5A, 0xE7,
  0x1A, 0xD0, 0x69, 0x87, 0x4F, 0xE3, 0xB5, 0x2C,
  0x7D, 0xE3, 0x06, 0x9A, 0x12, 0x85, 0xBC, 0x4F,
  0xD8, 0xB5, 0x6F, 0x03, 0x47, 0x2C, 0x1A, 0xE9,
  0xA6, 0x90, 0xCB, 0x7D, 0xF1, 0x3E, 0x52, 0x84,
  0x3F, 0x06, 0xA1, 0xD8, 0x94, 0x5B, 0xC7, 0x2E,
  0x2C, 0x41, 0x7A, 0xB6, 0x85, 0x3F, 0xD0, 0xE9,
  0xEB, 0x2C, 0x47, 0xD1, 0x50, 0xFA, 0x39, 0x86,
  0x42, 0x1B, 0xAD, 0x78, 0xF9, 0xC5, 0x63, 0x0E,
  0xB8, 0xC7, 0x1E, 0x2D, 0x6F, 0x09, 0xA4, 0x53,
  0xC1, 0xAF, 0x92, 0x68, 0x0D, 0x34, 0xE7, 0x5B,
  0xAF, 0x42, 0x7C, 0x95, 0x61, 0xDE, 0x0B, 0x38,
  0x9E, 0xF5, 0x28, 0xC3, 0x70, 0x4A, 0x1D, 0xB6,
  0x43, 0x2C, 0x95, 0xFA, 0xBE, 0x17, 0x60, 0x8D,
  0x4B, 0x2E, 0xF0, 0x8D, 0x3C, 0x97, 0x5A, 0x61,
  0xD0, 0xB7, 0x49, 0x1A, 0xE3, 0x5C, 0x2F, 0x86,
  0x14, 0xBD, 0xC3, 0x7E, 0xAF, 0x68, 0x05, 0x92,
  0x6B, 0xD8, 0x14, 0xA7, 0x95, 0x0F, 0xE2, 0x3C,
  0xD2, 0x84, 0x6F, 0xB1, 0xA9, 0x3E, 0x50, 0xC7,
  0x1F, 0xD8, 0xA3, 0x74, 0xC5, 0x6B, 0x0E, 0x92,
  0x7B, 0x41, 0x9C, 0xE2, 0x06, 0xAD, 0xF3, 0x58,
  0x21, 0xE7, 0x4A, 0x8D, 0xFC, 0x90, 0x35, 0x6B
]

# 7 bits - miss the last one.
def __expand_key(in_str):
  return [ord(i) - ord('0') for i in "".join([bin(ord(x))[2:-1].rjust(7,"0") for x in in_str])]

def expand_data(in_str):
  return [ord(i) - ord('0') for i in "".join([bin(ord(x))[2:].rjust(8,"0") for x in in_str])]

def expand_data_npz(in_str):
  l = [int(i) for i in "".join([bin(x)[2:].rjust(8,"0") for x in in_str])]
  return l

def permute(table,blk):
  return list([blk[x] for x in table])

# def permute(table,blk):
#   out = [0] * len(table)
#   for i in range(0,len(table)):
#     print table[i]
#     out[i] = blk[table[i]]
#   return out
 
def inv_permute(table,blk,default_char=2):
  pt = [default_char] * (max(table) + 1)
  for index in range(0,len(blk)):
    if pt[table[index]] == 2 or pt[table[index]] == 3:
      pt[table[index]] = int(blk[index])
    else:
      if pt[table[index]] != int(blk[index]):
        print("fail - mismatch in inv_permute")
        sys.exit(0)
  return pt

def mapToInteger(in_s,bits=6):
  in_r = in_s[::-1]
  out = 0
  for ix in range(0,bits):
    i = ix
    if (in_r[i] != 2) and (in_r[i] != 3):
      out += math.pow(2,i) * in_r[i]
    else:
      pass
  return out

def convertToSboxIndex(in_int):
  in_bin = [int(b) for b in bin(in_int)[2:].rjust(8,"0")]
  out_bin = [in_bin[2],in_bin[7],in_bin[3],in_bin[4],in_bin[5],in_bin[6]]
  return int(mapToInteger(out_bin))

# ORIG_KEY = [0x2b, 0x7e, 0x15, 0x16, 0x28, 0xae, 0xd2, 0xa6]

def bytesToBitstring(in_str):
  out = []
  for b in in_str:
    out += [ord(x) - ord('0') for x in bin(b)[2:].rjust(8,"0")]
  return out

def bitstringToBytes(in_str):
  return [int(mapToInteger(in_str[i:i + 8],8)) for i in range(0, len(in_str), 8)]

class desSplit:
  def __init__(self,pt):
    px = bytesToBitstring(pt)
    px_pc1 = permute(PC1TAB,px)
    # print len(px_pc1)
    shiftKeyL = px_pc1[:28]
    shiftKeyL.append( shiftKeyL[0] )
    del shiftKeyL[0]
    shiftKeyR = px_pc1[28:]
    shiftKeyR.append(shiftKeyR[0])
    del shiftKeyR[0]
    shiftedKey = shiftKeyL + shiftKeyR
    print(len(shiftedKey))
    px_pc2 = permute(PC2TAB,shiftedKey)
    px_bytes = bitstringToBytes(px_pc2)
    for x in px_bytes:   # we know the reference infrastructure is correct
      print("%02x" % x,)  # but there must be a correlated leak...

def stringify(hex_in):
  return "".join([chr(hexbyte) for hexbyte in hex_in])

class desRecombine:
  def __init__(self,pt):
    pt_temp = []
    for pt_byte in pt:
      pt_temp += [ord(x) - ord('0') for x in bin(pt_byte)[2:].rjust(6,"0")]
      # pt_temp += [0,0]
      # pt_temp += [px[0], px[2], px[3], px[4], px[5], px[1]]
    pt_temp_recovered = [int(mapToInteger(pt_temp[i:i + 8],8)) for i in range(0, len(pt_temp), 8)]
    # print [hex(i) for i in pt_temp_recovered]
    inv_pt = inv_permute(PC2TAB,pt_temp) # 48 bits in, 56 bits out
    # print inv_pt
    # print len(inv_pt)
    inv_pt_hexlify = [int(mapToInteger(inv_pt[i:i + 8],8)) for i in range(0, len(inv_pt), 8)]
    # print "INVERTED PC2"
    # print [hex(h) for h in inv_pt_hexlify]
    REAL_INVPC2 = [0xc0, 0x85, 0x66, 0x9d, 0x75, 0xc6, 0x7d]
    x = bytesToBitstring(REAL_INVPC2)
    for i in range(0,len(inv_pt)):
      if inv_pt[i] != x[i]:
        pass
        # print "mismatch!",
        # print inv_pt[i]
    # at this point, inv_pt is our "source material"
    inv_pt_L = inv_pt[:28]
    inv_pt_L = [inv_pt_L[27]] + inv_pt_L[:27]
    inv_pt_R = inv_pt[28:]
    inv_pt_R = [inv_pt_R[27]] + inv_pt_R[:27]
    inv_pt = inv_pt_L + inv_pt_R
    # print inv_pt
    # the last bit is always lost...
    inv_pc1 = inv_permute(PC1TAB,inv_pt,3) + [3]
    print(inv_pc1)
    # REAL_KEY = [0x2b, 0x7e, 0x15, 0x16, 0x28, 0xae, 0xd2, 0xa6]
    # real_exp = bytesToBitstring(REAL_KEY)
    # for i in range(0,len(real_exp)):
    #   if inv_pc1[i] != real_exp[i]:
    #     print "mismatch! %d" % inv_pc1[i]
    self.inv_pc1 = inv_pc1

  # input in bytestring format
  def bruteKey(self,knownPlain,knownCipher):
    for i in range(0,256):
      # print "TRYING %d" % i
      test_template = [ord(x) - ord('0') for x in bin(i)[2:].rjust(8,"0")]
      # print test_template
      try_key = [0] * len(self.inv_pc1)
      for tposn in range(0,len(self.inv_pc1)):
        if self.inv_pc1[tposn] == 2:
          try_key[tposn] = test_template.pop()
        elif try_key[tposn] == 3:
          self.inv_pc1[tposn] = 0
        else:
          try_key[tposn] = self.inv_pc1[tposn]
      # print try_key
      try_hexlified = bitstringToBytes(try_key)
      try_hexstr = "".join([chr(xt) for xt in try_hexlified])
      # print binascii.hexlify(try_hexstr)
      d = DES.new(try_hexstr,DES.MODE_ECB)
      if d.encrypt(stringify(knownPlain)) == stringify(knownCipher):
        print("GOTCHA: %s" % binascii.hexlify(try_hexstr))
      # else:
      #   print binascii.hexlify(d.encrypt(stringify(knownPlain)))

class desIntermediateValue:
  def __init__(self):
    self.cumulative = 0
    self.disableCumulative = False
    pass

  def preprocess(self,MyPT):
    d = permute(IPTAB,expand_data_npz(MyPT))
    d_ex = permute(ETAB,d[32:])
    self.d_ex = [d_ex[i:i+6] for i in range(0,len(d_ex),6)]

  def generateSbox(self,byte_posn,key):
    tmp_d = int(mapToInteger(self.d_ex[byte_posn]))
    tmp_d ^= int(key) 
    tmp_d_bin = [ord(b) - ord("0") for b in bin(tmp_d)[2:].rjust(6,"0")]
    n = (tmp_d_bin[0] << 5) + (tmp_d_bin[5] << 4) + (tmp_d_bin[1] << 3) + (tmp_d_bin[2] << 2) + (tmp_d_bin[3] << 1) + tmp_d_bin[4]
    x = SBOX[(n >> 1) + (byte_posn * 32)]
    if n % 2 == 1:
      x = x & 0x0F
    else:
      x = x >> 4
    if self.disableCumulative:
      return x
    if byte_posn == 0:
      return x
    else:
      x_cumulative = self.cumulative << 4
      x_cumulative |= x
      x_cumulative &= 0xFF
      return x_cumulative

  def saveCumulative(self,byte_posn,key):
    self.cumulative = self.generateSbox(byte_posn,key)
  
TEST_KEY = [0x3f, 0x3f, 0x3f, 0x2f, 0x20, 0x10, 0x1f]

def test_splitin6bits():
  pass

# 2a7e141628aed2a6
# 2b7e151628aed2a6

if __name__ == "__main__":
  RECOVERED = [0x22, 0x10, 0x30, 0x21, 0x32, 0x38, 0x07, 0x3f]
  d = desRecombine(RECOVERED)
  d.bruteKey([0xFF, 0xFF, 0xFF, 0xFF, 0xAA, 0xAA, 0xAA, 0xAA],[0x51,0x0e,0xd9,0x41,0xf4, 0x63, 0x31, 0x9b])
