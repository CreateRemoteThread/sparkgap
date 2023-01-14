#!/usr/bin/env python3

from drivers import base
import random
import time
import serial

# standard uart interface
# k[hexstring] = set key, return k[newkey]
# e[hexstring] = do encrypt, return e[result]

class DriverInterface(base.BaseDriverInterface):
  def __init__(self):
    super().__init__()
    self.config = {}
    print("Using Simple UART driver")
    # reserved names: samplecount,tracecount,trigger
    pass

  def init(self,frontend=None):
    print("initializing uart")
    self.ser = serial.Serial("/dev/ttyUSB0",9600,timeout=1.0)
    self.ser.write(b"\n")
    self.frontend = frontend
    pass

  def drive(self,in_text=None):
    next_rand = [int(random.uniform(0,256)) for _ in range(0,16)]
    next_key = [int(random.uniform(0,256)) for _ in range(0,16)]
    if "rekey" in self.config.keys():
      print("Re-keying...")
      self.ser.write(b"k")  
      self.ser.write(b"".join([b"%02x" % nr for nr in next_key]))
      self.ser.write(b"\n")
      time.sleep(0.25)
      f = self.ser.read(16+36)
      while self.ser.in_waiting:
        f += self.ser.read(1)
        time.sleep(0.01)
      print("KEY: %s" % f)
    self.frontend.arm()
    if "stm32_fix" in self.config.keys():
      print("using stm32 fix")
      wait_time = float(self.config["stm32_fix"])
      time.sleep(wait_time)
    time.sleep(0.5)
    self.ser.write(b"e")
    self.ser.write(b"".join([b"%02x" % nr for nr in next_rand]))
    self.ser.write(b"\n")
    print("Written")
    f = self.ser.read(16+36)
    while self.ser.in_waiting:
      f += self.ser.read(1)
      time.sleep(0.01)
    print("OK: %s" % f)
    # f = f.strip().split("+e")[1]
    # b'++++++++++++++++e9501ed06d55029667d11c338baeab7eb\r\n'
    if b'+e' in f:
      next_ct = f[17:49]
      next_ct = [int(next_ct[i:i+2],16) for i in range(0,len(next_ct),2)]
    else:
      next_ct = f[1:33]
      next_ct = [int(next_ct[i:i+2],16) for i in range(0,len(next_ct),2)]
    text_rand = "".join(["%02x" % nr for nr in next_rand])
    text_ct = "".join(["%02x" % nr for nr in next_ct])
    if "rekey" in self.config.keys():
      text_key = "".join(["%02x" % nr for nr in next_key])
      print("Ok (rekey), saving %s:%s" % (text_rand,text_key)) 
      return (next_rand,next_key)
    else:
      print("Ok (samekey), saving %s:%s" % (text_rand,text_ct)) 
      return (next_rand,next_ct)


  def close(self):
    self.ser.close()
    pass
