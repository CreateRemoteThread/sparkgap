#!/usr/bin/env python3

import sparkgap.filemanager
import sys

def keeloqNLF_SLOW(a, b, c, d, e):
  return (d + e + a & c + a & e + b & c + b & e + c & d + d & e + a & d & e + a & c & e + a & b & d + a & b & c) % 2;

def keeloqNLF(a, b, c, d, e):
  return (d + e + a * c + a * e + b * c + b * e + c * d + d * e + a * d * e + a * c * e + a * b * d + a * b * c) % 2;

def keeloqDecryptCalcLSB(data, keybit):
  nlf = keeloqNLF((data>>30)%2, (data>>25)%2, (data>>19)%2, (data>>8)%2, (data>>0)%2)
  lsb = (keybit ^ (data>>31) ^ (data>>15) ^ nlf) % 2
  return lsb

def keeloqDecryptKeybit(data, keybit):
  return ((data & 0x7FFFFFFF)<<1) ^ keeloqDecryptCalcLSB(data, keybit)

def keeloqFullDecrypt(data,keyBits):
  decr = data
  # print(keyBits)
  for i in range(0,528):
    decr = keeloqDecryptKeybit(decr,keyBits[i % 64])
  return decr

if len(sys.argv) != 2:
  print("usage: ./keeloq_brute.py [trace_set]")
  sys.exit(0)

def unpackKeeloq(plaintext):
  out = ""
  for i in range(0,9):
    out = format(plaintext[i],"08b") + out
  return out[6:]

def unpackKeeloqInt(plaintext):
  ival = unpackKeeloq(plaintext)
  nextstep = ival[0:32]
  return int(nextstep[::-1],2)

fn = sparkgap.filemanager.TraceManager(sys.argv[1])
transmits = fn.loadPlaintexts()

CT0 = unpackKeeloqInt(transmits[0])
CT1 = unpackKeeloqInt(transmits[1])
CT2 = unpackKeeloqInt(transmits[2])

BITMASK = 0b11110011111111110000000000000000
for i in range(0,0x100000000):
  if i % 0x10000000 == 0:
    print("First byte moving forward.")
  wholeKey = 0x0218debd * 0x100000000 + i
  kb = [ord(kbit) - ord('0') for kbit in  format(wholeKey,"064b")]
  PT0 = keeloqFullDecrypt(CT0,kb)
  PT1 = keeloqFullDecrypt(CT1,kb)
  if PT0 & BITMASK == PT1 & BITMASK:
    print("%08x" % wholeKey)
    print("Decryption:")
    print("PT0:%04x" % PT0)
    print("PT1:%04x" % PT1)
    PT2 = keeloqFullDecrypt(CT2,kb)
    print("PT2:%04x" % PT2)
    if PT2 & BITMASK == PT1 & BITMASK:
      print("LIKELY KEY CANDIDATE")
