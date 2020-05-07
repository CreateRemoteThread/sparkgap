#!/usr/bin/env python3

from smartcard.CardType import AnyCardType
from smartcard.CardRequest import CardRequest
from smartcard.CardConnectionObserver import ConsoleCardConnectionObserver
from smartcard.Exceptions import CardRequestTimeoutException
import random

class SIMController:
  def __init__(self):
    self.c = None      # fuck pyscard. seriously.
    pass

  def french_apdu(self,rand=None,autn=None,scope=None,debug=False,trigger=None):
    if trigger is not None:
      trigger.disarm()
    self.cardrequest = CardRequest(timeout=5,cardType=AnyCardType())
    self.cardservice = self.cardrequest.waitforcard()
    if debug:
      obs = ConsoleCardConnectionObserver()
      self.cardservice.connection.addObserver(obs)
    self.cardservice.connection.connect()
    self.c = self.cardservice.connection
    r,sw1,sw2 = self.c.transmit([0x00, 0xa4, 0x08, 0x04, 0x02, 0x2f, 0x00])
    r,sw1,sw2 = self.c.transmit([0x00,0xC0,0x00,0x00] + [sw2])
    r,sw1,sw2 = self.c.transmit([0x00,0xB2,0x01,0x04] + [r[7]])
    r,sw1,sw2 = self.c.transmit([0x00,0xA4,0x04,0x04] + list(r[3:4 + r[3]]))
    r,sw1,sw2 = self.c.transmit([0x00,0xC0,0x00,0x00] + [sw2])
    if rand is None and autn is None:
      authcmd = [0x00, 0x88, 0x00, 0x81, 0x22, 0x10] + [0xaa] * 16 + [0x10] + [0xbb] * 16
    else:
      authcmd = [0x00, 0x88, 0x00, 0x81, 0x22, 0x10] + rand + [0x10] + autn
    if trigger is not None:
      trigger.arm()
    scope.arm()
    r,sw1,sw2 = self.c.transmit(authcmd)

  def nextg_apdu(self,rand=None,autn=None,debug=False,trigger=None,scope=None):
    if trigger is not None:
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
    if trigger is not None:
      trigger.arm()
    scope.arm()
    r,sw1,sw2 = self.c.transmit(authcmd)


class DriverInterface():
  def __init__(self):
    self.config = {}
    self.config["trigger"] = None
    print("Using Smartcard Driver")

  def init(self,scope):
    print("Smartcard: initializing")
    self.sc = SIMController()
    self.scope = scope
     
  def drive(self,data_in = None):
    next_rand = [random.randint(0,255) for _ in range(16)]
    next_autn = [random.randint(0,255) for _ in range(16)]
    # self.sc.french_apdu(next_rand,next_autn,self.scope,trigger=self.config["trigger"])
    self.sc.nextg_apdu(next_rand,next_autn,scope=self.scope,trigger=self.config["trigger"])
    return (next_rand,next_autn)

  def close(self):
    pass
