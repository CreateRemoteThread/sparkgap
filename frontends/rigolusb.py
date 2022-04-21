#!/usr/bin/env python3

import os
import sys
import binascii
import time
import struct
import os
import time

class RigolUSBTMC:
  SLEEPTIME_BEFORE_WRITE = 0E-3
  SLEEPTIME_AFTER_WRITE = 5E-3
  SLEEPTIME_BEFORE_READ = 5E-3
  SLEEPTIME_AFTER_READ = 5E-3

  def __init__(self,device="/dev/usbtmc0"):
    self.FILE = os.open(device,os.O_RDWR)
  
  def write_raw(self,command):
    time.sleep(self.SLEEPTIME_BEFORE_WRITE)
    os.write(self.FILE,command)
    time.sleep(self.SLEEPTIME_AFTER_WRITE)
  
  def read_raw(self,num=-1,timeout=0.):
    if num == -1:
      num = 1024 * 1024 + 1024
    time.sleep(self.SLEEPTIME_BEFORE_READ)
    ret = os.read(self.FILE,num)
    time.sleep(self.SLEEPTIME_AFTER_READ)
    return ret

  @property
  def waveform_preamble(self):
    values = self.ask_raw(b":WAV:PRE?")
    values = values.split(b",")
    print(values)
    assert len(values) == 10
    fmt, typ, pnts, cnt, xref, yorig, yref  = (int(val) for val in values[:4] + values[6:7] + values[8:10])
    xinc, xorig, yinc = (float(val) for val in values[4:6] + values[7:8])
    return (fmt, typ, pnts, cnt, xinc, xorig, xref, yinc, yorig, yref)

  @property
  def waveform_preamble_dict(self):
    keys = 'fmt, typ, pnts, cnt, xinc, xorig, xref, yinc, yorig, yref'.split(', ')
    return dict(list(zip(keys, self.waveform_preamble)))

  def ask_raw(self,query):
    self.write_raw(query)
    return self.read_raw()

  def __del__(self):
    try:
      os.close(self.FILE)
    except:
      pass 

class CaptureInterface():
  def __init__(self):
    print("RigolUSB: Using Rigol USB interface")
    self.config = {}
    self.config["samplecount"] = 15000

  def init(self):
    print("RigolUSB: Connect and configure")
    self.scope = RigolUSBTMC()
    self.scope.write_raw(b":STOP")
    self.scope.write_raw(b":TRIG:MODE EDGE")
    self.scope.write_raw(b":TRIG:EDGE:SWE SING")

  def arm(self):
    print("RigolUSB: get memory depth")
    mdepth = self.scope.ask_raw(b":ACQ:MDEP?")
    if mdepth == b"AUTO\n":
      print("RigolUSB: fucking rigol, going for preamble method")
      self.mdepth = self.scope.waveform_preamble_dict["pnts"]
    else:
      print("RigolUSB: got an actual mdepth")
      self.mdepth = int(float(mdepth))
    print("RigolUSB: arm (single), memory depth is %d samples" % self.mdepth)
    self.scope.write_raw(b":SING")

  def decode_ieee_block(self,ieee_bytes):
    n_header_bytes = int(chr(ieee_bytes[1])) + 2
    n_data_bytes = int(ieee_bytes[2:n_header_bytes].decode('ascii'))
    return ieee_bytes[n_header_bytes:n_header_bytes + n_data_bytes]

  def capture(self):
    self.scope.write_raw(b":WAV:SOUR CHAN1")
    self.scope.write_raw(b":WAV:MODE RAW")
    self.scope.write_raw(b":WAV:FORM BYTE")
    self.scope.write_raw(b":WAV:DATA?")
    pos = self.mdepth // 2
    end = pos + self.config["samplecount"]
    buff = b""
    pnts = end - pos - 1
    max_byte_len = 250000
    while len(buff) < pnts:
      print("len(buff) is %d" % len(buff))
      print("End: %d" % end)
      print("Pos + Pnts: %d" % (pos + pnts))
      print("Pos + max_byte_len - 1: %d" % (pos + max_byte_len - 1))
      end_pos = min([pos + pnts, pos + max_byte_len - 1, end])
      self.scope.write_raw(b":WAV:STAR %d" % pos)
      self.scope.write_raw(b":WAV:STOP %d" % end_pos)
      self.scope.write_raw(b":WAV:DATA?")
      time.sleep(0.5)
      print("LOG: %d -> %d" % (pos,end_pos))
      data = self.scope.read_raw(-1)
      buff += self.decode_ieee_block(data)
      while not data.endswith(b"\n"):
        time.sleep(0.5)
        print("Reading")
        data += self.scope.read_raw(-1)
        buff += self.decode_ieee_block(data)
      pos += max_byte_len
    print("STOP")
    # x = input(" > ")
    samples = list(struct.unpack(str(len(buff))+'B', buff))
    return samples

  def close(self):
    del self.scope
