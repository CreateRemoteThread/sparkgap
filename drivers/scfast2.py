#!/usr/bin/env python3

from drivers import base
import random
import time
import serial

class SIMController2:
  def __init__(self):
    self.ser = serial.Serial("/dev/ttyUSB0",9600)

  def _do_auth(self):
    pass

  def _set_wait_us(self,wait_time):
    self.ser.write(b'w')
    self.ser.write(bytes([(wait_time >> 8) & 0xFF]));
    self.ser.write(bytes([wait_time & 0xFF]));
    c = self.ser.read(1)
    b1 = self.ser.read(1)
    b2 = self.ser.read(1)
    print(c)
    print("%02x" % b1[0])
    print("%02x" % b2[0])
    return
    

  def _set_wait_ms(self,wait_time):
    self.ser.write(b'W')
    self.ser.write(bytes([(wait_time >> 8) & 0xFF]));
    self.ser.write(bytes([wait_time & 0xFF]));
    c = self.ser.read(1)
    b1 = self.ser.read(1)
    b2 = self.ser.read(1)
    print(c)
    print("%02x" % b1[0])
    print("%02x" % b2[0])
    return
 
  def _send_apdu(self,apdu):
    self.ser.write(b'a')
    self.ser.write(bytes([len(apdu)]))
    self.ser.write(apdu)

  def _select_file(self,file_id=None,aid=[],extra_delay=None):
    cmd = [0xa0, 0xa4, 0x00, 0x00, 0x02]
    USIM_CLA = 0x00
    cmd[0] = USIM_CLA
    cmd[3] = 0x04
    if len(aid) != 0:
      cmd[2] = 0x04
      cmd[4] = len(aid)
      cmd += aid
    else:
      b1 = (file_id >> 8) & 0xFF
      b2 = file_id & 0xFF
      cmd += [b1,b2]
    out = ""
    for c in cmd:
      out += "%02x " % c
    print(out)
    self._send_apdu(cmd)
    if extra_delay is not None:
      time.sleep(extra_delay)
    return self._readbuf()

  def _get_response(self,size):
    cmd = [0x00,0xC0,0x00,0x00]
    cmd += [size]
    out = ""
    for c in cmd:
      out += "%02x " % c
    print(out)
    self._send_apdu(cmd)
    time.sleep(0.1)
    return self._readbuf()

  def _readbuf(self):
    time.sleep(0.1)
    self.ser.write(b'd')
    c = self.ser.read(1)
    if c != b'#':
      print("Expected #, got %02x" % ord(c))
      # return
    respsize = ord(self.ser.read(1))
    print("RESPSIZE %d" % respsize)
    c = self.ser.read(respsize)
    out = ""
    for cx in c:
      out += "%02x " % cx
    print(out)
    time.sleep(0.1)
    return c

  def _umts_auth(self,rand,autn):
    cmd = [0x00, 0x88, 0x00, 0x81, 0x22]
    cmd.append(len(rand))
    cmd += rand
    cmd.append(len(autn))
    cmd += autn
    self._send_apdu(cmd)

class DriverInterface(base.BaseDriverInterface):
  def __init__(self):
    super().__init__()
    self.config = {}
    self.config["trigger"] = None
    print("Using SCFast Driver")

  def init(self,scope):
    print("SCFast: initializing")
    self.sc = SIMController2()
    self.scope = scope
    print("Reset")
    self.sc.ser.write(b'R')
    self.sc.ser.read(1)
    time.sleep(0.5)
    print("Grabbing APDU")
    self.sc._readbuf()
    time.sleep(0.1)
    self.sc._set_wait_us(0x0000)
    self.sc._set_wait_ms(0x0000)
    r = self.sc._select_file(file_id=0x2F00)
    r = self.sc._readbuf()
    r = self.sc._get_response(r[1])
    r = self.sc._send_apdu([0x00,0xB2,0x01,0x04,r[8]])
    time.sleep(0.1)
    r = self.sc._readbuf()
    r = self.sc._select_file(aid=r[5:5+r[4]],extra_delay=0.5)
    print("3G SELECTED")
    time.sleep(0.1)
    # r = self.sc._readbuf()
    # r = self.sc._get_response(r[2]) # this does 0x61, blah
    time.sleep(0.1)
    r = self.sc._select_file(file_id = 0x6F07)
    time.sleep(0.1)
    r = self.sc._readbuf()
    r = self.sc._get_response(r[1])
    print("SENDING READBINARY CMD")
    r = self.sc._send_apdu([0x00,0xB0,0x00,0x00,0x09])
    time.sleep(0.1)
    r = self.sc._readbuf()
    if 0x6C in r:
      print("READBINARY LENGHT ERROR")
    # r = self.sc._get_response(r[1])
    # time.sleep(0.1)
    print("AUTH")

  def drive(self,data_in = None):
    return self.drive_efdir(data_in)

  def drive_efdir(self,data_in = None):
    if data_in is None:
      next_rand = [random.randint(0,255) for _ in range(16)]
    else:
      print("TLVA!")
      next_rand = data_in
    next_autn = [random.randint(0,255) for _ in range(16)]
    self.sc._set_wait_ms(0x000a * 2)
    time.sleep(0.1)
    self.scope.arm()
    self.sc._umts_auth([0xaa] * 16, [0xbb] * 16)
    time.sleep(0.1)
    r = self.sc._readbuf()
    return (next_rand,next_autn)

  def close(self):
    pass
