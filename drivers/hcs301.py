#!/usr/bin/env python3

from drivers import base
import random
import time
import serial
import binascii

def packKeeloq(bitstring):
  bs = int(bitstring,2)
  out = [0] * 16
  for i in range(0,9):
    fq = (bs >> (i * 8)) & 0xFF
    out[i] = fq
  return out

class DriverInterface(base.BaseDriverInterface):
  def __init__(self):
    super().__init__()
    self.config = {}
    self.config["trigger"] = None
    print("Using HCS301 Driver")

  def init(self,scope):
    self.scope = scope
    print("HCS301: initializing")
    self.ser = serial.Serial("/dev/ttyUSB0",115200)

  # fix this later - for now just do even/odd.
  def drive(self,data_in = None):
    self.ser.flush()
    self.scope.arm()
    time.sleep(0.5)
    self.ser.write(b"b")
    fd = self.ser.read(66)
    c = self.ser.read(1)
    print(c)
    self.ser.read(2)
    # fd = fd[0:32]
    # fi = int(fd[::-1],2)
    # print("%x:%s" % (fi,fd))
    # printf(fi,fd)
    # fr = [fi & 0xFF, (fi >> 8) & 0xFF, (fi >> 16) & 0xFF] + [0] * 13
    return (packKeeloq(fd),[0] * 16)
    # if fd[0] == ord('1'):
    #   return ([1] * 16,[0] * 16)
    # else:
    #   return ([0] * 16,[0] * 16)

  def close(self):
    pass
