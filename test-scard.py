#!/usr/bin/env python3
    

from smartcard.CardType import AnyCardType
from smartcard.CardRequest import CardRequest
from smartcard.CardConnectionObserver import ConsoleCardConnectionObserver
from smartcard.Exceptions import CardRequestTimeoutException
import triggerbuddy
import getopt
import sys
import uuid
import random
import numpy as np
import random
import serial

class SIMController:
  def __init__(self,trigger=None):
    self.c = None
    self.t = trigger

  def do_auth(self,debug=True):
    if self.t:
      t.disarm()
    self.cardrequest = CardRequest(timeout=5,cardType=AnyCardType())
    self.cardservice = self.cardrequest.waitforcard()
    if debug:
      obs = ConsoleCardConnectionObserver()
      self.cardservice.connection.addObserver(obs)
    self.cardservice.connection.connect()
    self.c = self.cardservice.connection
    print("ATR : %s" % self.cardservice.connection.getATR())
    r,sw1,sw2 = self._select_file(file_id=0x3F00)                 # SCARD_FILE_MF
    r,sw1,sw2 = self._select_file(aid=[0xa0,0x00,0x00,0x00,0x87]) # default 3G file
    next_rand = [random.randint(0,255) for _ in range(16)]
    next_autn = [random.randint(0,255) for _ in range(16)]
    str_rand = "".join(["%02x" % _ for _ in next_rand])
    str_autn = "".join(["%02x" % _ for _ in next_autn])
    print("%s:%s" % (str_rand,str_autn))
    # self.t.arm()
    r,sw1,sw2 = self._umts_auth(next_rand,next_autn)
    # if sw1 == 0x61:
    #   self._get_response(sw2)

  def _umts_auth(self,rand,autn):
    cmd = [0x00, 0x88, 0x00, 0x81, 0x22]
    cmd.append(len(rand))
    cmd += rand
    cmd.append(len(autn))
    cmd += autn
    dx = triggerbuddy.edgeCount(cmd)
    self.t.processCommand("io %d" % dx)
    self.t.arm()
    r,sw1,sw2 = self.c.transmit(cmd)
    return (r,sw1,sw2)

  def _get_response(self,resp_length):
    USIM_CLA = 0x00
    get_resp = [0xa0, 0xc0, 0x00, 0x00]
    get_resp[0] = USIM_CLA
    get_resp.append(resp_length)
    r,sw1,sw2 = self.c.transmit(get_resp)
    return r,sw1,sw2

  def _select_file(self,file_id=None,aid=[]):
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
    r,sw1,sw2 = self.c.transmit(cmd)
    return (r,sw1,sw2)

class SIMController2:
  def __init__(self):
    self.ser = serial.Serial("/dev/ttyUSB0",9600)

  def _do_auth(self):
    pass
    
  def _send_apdu(self,apdu):
    self.ser.write(b'a')
    self.ser.write(bytes([len(apdu)]))
    self.ser.write(apdu)

  def _select_file(self,file_id=None,aid=[]):
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
    # r,sw1,sw2 = self.c.transmit(cmd)
    # return (r,sw1,sw2)

  def _get_resp(self):
    self.ser.write(b'd')
    c = self.ser.read(1)
    if c != b'#':
      print("Expected #, got %02x" % ord(c))
      return
    respsize = ord(self.ser.read(1))
    print("RESPSIZE %d" % respsize)
    c = self.ser.read(respsize)
    for cx in c:
      print("R: %02x" % cx)

  def _umts_auth(self,rand,autn):
    cmd = [0x00, 0x88, 0x00, 0x81, 0x22]
    cmd.append(len(rand))
    cmd += rand
    cmd.append(len(autn))
    cmd += autn
    self._send_apdu(cmd)
    # r,sw1,sw2 = self.c.transmit(cmd)
    # return (r,sw1,sw2)
    
import time
if __name__ == "__main__":
  print(" >> YOU MUST MANUALLY CAPTURE ON YOUR SCOPE <<") 
  print(" >> NO SCOPE AUTOMATION ON C = 1 <<") 
  sc = SIMController2()
  time.sleep(0.5)
  # sc._select_file(file_id=0x3F00)
  # time.sleep(1.0)
  sc._select_file(aid=[0xa0,0x00,0x00,0x00,0x87])
  time.sleep(0.5)
  next_rand = [random.randint(0,255) for _ in range(16)]
  next_autn = [random.randint(0,255) for _ in range(16)] 
  sc._umts_auth(next_rand,next_autn)
  time.sleep(0.5)
  sc._get_resp()
  time.sleep(0.1)
  sc.ser.close()
  sys.exit(0)
