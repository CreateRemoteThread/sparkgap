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

class SIMController:
  def __init__(self):
    self.c = None      # fuck pyscard. seriously.
    pass

  def french_apdu(self,rand=None,autn=None,debug=False,trigger=None):
    # trigger.disarm()
    self.cardrequest = CardRequest(timeout=5,cardType=AnyCardType())
    self.cardservice = self.cardrequest.waitforcard()
    if debug:
      obs = ConsoleCardConnectionObserver()
      self.cardservice.connection.addObserver(obs)
    self.cardservice.connection.connect()
    self.c = self.cardservice.connection
    # print(" !!! USING SHORTER SSTIC2018 PAPER APDU SEQUENCE !!!")
    r,sw1,sw2 = self.c.transmit([0x00, 0xa4, 0x08, 0x04, 0x02, 0x2f, 0x00])
    r,sw1,sw2 = self.c.transmit([0x00,0xC0,0x00,0x00] + [sw2])
    r,sw1,sw2 = self.c.transmit([0x00,0xB2,0x01,0x04] + [r[7]])
    r,sw1,sw2 = self.c.transmit([0x00,0xA4,0x04,0x04] + list(r[3:4 + r[3]]))
    r,sw1,sw2 = self.c.transmit([0x00,0xC0,0x00,0x00] + [sw2])
    if rand is None and autn is None:
      authcmd = [0x00, 0x88, 0x00, 0x81, 0x22, 0x10] + [0xaa] * 16 + [0x10] + [0xbb] * 16
    else:
      authcmd = [0x00, 0x88, 0x00, 0x81, 0x22, 0x10] + rand + [0x10] + autn
    # trigger.arm()
    r,sw1,sw2 = self.c.transmit(authcmd)

  def nextg_apdu(self,rand=None,autn=None,debug=False,trigger=None):
    trigger.disarm()
    self.cardrequest = CardRequest(timeout=5,cardType=AnyCardType())
    self.cardservice = self.cardrequest.waitforcard()
    if debug:
      obs = ConsoleCardConnectionObserver()
      self.cardservice.connection.addObserver(obs)
    self.cardservice.connection.connect()
    self.c = self.cardservice.connection
    # print("ATR... : %s" % self.cardservice.connection.getATR())
    r,sw1,sw2 = self.c.transmit([0x00, 0xa4, 0x08, 0x04, 0x02, 0x2f, 0x00])
    r,sw1,sw2 = self.c.transmit([0x00, 0xc0, 0x00, 0x00, sw2])
    r,sw1,sw2 = self.c.transmit([0x00, 0xb2, 0x01, 0x04, r[7]])
    r,sw1,sw2 = self.c.transmit([0x00,0xA4,0x04,0x04] + list(r[3:4 + r[3]]))
    r,sw1,sw2 = self.c.transmit([0x00,0xC0,0x00,0x00] + [sw2])
    r,sw1,sw2 = self.c.transmit([0x00,0xA4,0x00,0x04,0x02,0x6F,0x07])
    r,sw1,sw2 = self.c.transmit([0x00, 0xc0, 0x00, 0x00, sw2])
    # r,sw1,sw2 = self.c.transmit([0x00, 0xb0, 0x00, 0x00, r[7]])
    # r,sw1,sw2 = 
    # r,sw1,sw2 = self.c.transmit([0x00, 0xb2, 0x01, 0x04, r[7]])
    if rand is None and autn is None:
      authcmd = [0x00, 0x88, 0x00, 0x81, 0x22, 0x10] + [0xaa] * 16 + [0x10] + [0xbb] * 16
    else:
      authcmd = [0x00, 0x88, 0x00, 0x81, 0x22, 0x10] + rand + [0x10] + autn
    trigger.arm()
    print("Arming")
    r,sw1,sw2 = self.c.transmit(authcmd)

  def fuzzFile(self,observer=False):
    self.cardrequest = CardRequest(timeout=5,cardType=AnyCardType())
    self.cardservice = self.cardrequest.waitforcard()
    if observer:
      obs = ConsoleCardConnectionObserver()
      self.cardservice.connection.addObserver(obs)
    self.cardservice.connection.connect()
    self.c = self.cardservice.connection
    print("ATR... : %s" % self.cardservice.connection.getATR())
    print("Brute forcing...")
    out = ""
    for i in range(0,0xFF):
      for x in range(0,0xFF):
        response, sw1, sw2 = self.cardservice.connection.transmit([0x00,0xA4,0x08,0x04,0x02, i,x])
        if sw1 == 0x61:
          out += "Valid APDU from MF: %02x::%02x\n" % (i,x)
    return out

if __name__ == "__main__":
  sc = SIMController()
  t = triggerbuddy.TriggerBuddy()
  # t.processCommand("io 1")
  t.processCommand("io 1")
  t.processCommand("clk 48000") # nextg
  t.processCommand("ns 1") # nextg
  # t.processCommand("clk 48000") # purple
  print(" >> YOU MUST MANUALLY CAPTURE ON YOUR SCOPE <<") 
  print(" >> NO SCOPE AUTOMATION ON C = 1 <<") 
  next_rand = [random.randint(0,255) for _ in range(16)]
  next_autn = [random.randint(0,255) for _ in range(16)]
  str_rand = "".join(["%02x" % _ for _ in next_rand])
  str_autn = "".join(["%02x" % _ for _ in next_autn])
  print("%s:%s" % (str_rand,str_autn))
  # sc.french_apdu(next_rand,next_autn,debug=True,trigger=None)
  sc.nextg_apdu(next_rand,next_autn,debug=True,trigger=t)
  sys.exit(0)
