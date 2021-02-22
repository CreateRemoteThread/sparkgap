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
    # print(c)
    # print("%02x" % b1[0])
    # print("%02x" % b2[0])
    return
    

  def _set_wait_ms(self,wait_time):
    self.ser.write(b'W')
    self.ser.write(bytes([(wait_time >> 8) & 0xFF]));
    self.ser.write(bytes([wait_time & 0xFF]));
    c = self.ser.read(1)
    b1 = self.ser.read(1)
    b2 = self.ser.read(1)
    # print(c)
    # print("%02x" % b1[0])
    # print("%02x" % b2[0])
    return
 
  def _send_apdu(self,apdu):
    out = "SEND: "
    for c in apdu:
      out += "%02x " % c
    print(out)
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
    # out = ""
    # for c in cmd:
    #   out += "%02x " % c
    # print(out)
    self._send_apdu(cmd)
    if extra_delay is not None:
      time.sleep(extra_delay)
    return self._readbuf()

  def _get_response(self,size):
    cmd = [0x00,0xC0,0x00,0x00]
    cmd += [size]
    # out = ""
    # for c in cmd:
    #   out += "%02x " % c
    # print(out)
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

print("Begin SIM Explore")

