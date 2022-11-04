#!/usr/bin/env python3

import cProfile
import sys
import binascii
import funcs
import random
import time

def array_xor(a1,a2):
  return [a1[i] ^ a2[i] for i in range(0,len(a1))]

print("Initializing mixColumn(mask) for all fault masks")
mixedMaskDB = {}
for pos in range(0,4):
  for i in range(1,255):
    f_mask = [0] * 16
    f_mask[pos] = i
    f_out = funcs.mixcolumns(f_mask)
    mixedMaskDB[f_out[0] * 0x1000000 + f_out[1] * 0x10000 + f_out[2] * 0x100 + f_out[3]] = (pos,i)

def extractDiagonal(data):
  return [data[0],data[13],data[10],data[7]]

i_sbox = funcs._i_sbox

def solveDFA(fn):
  dl = []
  f = open("save.lst","w")
  global mixedMaskDB
  f_list = mixedMaskDB.keys()
  df = open(fn,"r")
  baseline = binascii.unhexlify(df.readline().rstrip())
  faulted = binascii.unhexlify(df.readline().rstrip())
  # df.close()
  print("Baseline: %s" % binascii.hexlify(baseline))
208 packages can be upgraded. Run 'apt list --upgradable  print("Faulted: %s" % binascii.hexlify(faulted))
  base = funcs.inv_shiftrows(list(baseline))[0:4]
  fault = funcs.inv_shiftrows(list(faulted))[0:4]
  for k0 in range(0,255):
    print("+, k0 is %d, time is %s, candidates = %d" % (k0,time.time(), len(dl)))
    for k1 in range(0,255):
      for k2 in range(0,255):
        for k3 in range(0,255):
          # key = (k0,k1,k2,k3)
          base_int = i_sbox[k0 ^ base[0]] * 0x1000000  + i_sbox[k1 ^ base[1]] * 0x10000 + i_sbox[k2 ^ base[2]] * 0x100 + i_sbox[k3 ^ base[3]]
          fault_int = i_sbox[k0 ^ fault[0]] * 0x1000000 + i_sbox[k1 ^ fault[1]] * 0x10000 +  i_sbox[k2 ^ fault[2]] * 0x100 +  i_sbox[k3 ^ fault[3]]
          if base_int ^ fault_int in f_list:
            dl.append( (k0,k1,k2,k3) )
            f.write( "%02x%02x%02x%02x\n" % (k0,k1,k2,k3))
            print("Match!")
  faulted = binascii.unhexlify(df.readline().rstrip())
  fault = funcs.inv_shiftrows(list(faulted))[0:4]
  dl2 = []
  for a in dl:
    (k0,k1,k2,k3) = a
    base_int = i_sbox[k0 ^ base[0]] * 0x1000000  + i_sbox[k1 ^ base[1]] * 0x10000 + i_sbox[k2 ^ base[2]] * 0x100 + i_sbox[k3 ^ base[3]]
    fault_int = i_sbox[k0 ^ fault[0]] * 0x1000000 + i_sbox[k1 ^ fault[1]] * 0x10000 +  i_sbox[k2 ^ fault[2]] * 0x100 +  i_sbox[k3 ^ fault[3]]
    if base_int ^ fault_int in f_list:
      dl2.append( (k0,k1,k2,k3) )
      print("Stage 2 Match!: %02x %02x %02x %02x" % (k0,k1,k2,k3))
  df.close()
  f.close()

if __name__ == "__main__" and len(sys.argv) == 2:
  cProfile.run("solveDFA(sys.argv[1])")
else:
  print("bye")
