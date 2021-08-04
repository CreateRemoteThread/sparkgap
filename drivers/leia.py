#!/usr/bin/env python3

import time
import random
from drivers import base
from smartleia import APDU,TriggerPoints,LEIA
from smartleia import create_APDU_from_bytes

class Fuck:
  def __init__(self):
    pass

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
    return cmd

  def _umts_auth(self,rand,autn):
    cmd = [0x00, 0x88, 0x00, 0x81, 0x22]
    cmd.append(len(rand))
    cmd += rand
    cmd.append(len(autn))
    cmd += autn
    return cmd

def send_and_get_resp(reader,byte_array):
  apdu = create_APDU_from_bytes(byte_array)
  r = reader.send_APDU(create_APDU_from_bytes(byte_array))
  # print(r)
  if r.sw1 == 0x61:
    apdu = APDU(cla=apdu.cla,ins=0xc0,p1=0x00,p2=0x00,le=r.sw2,send_le=1)
    r = reader.send_APDU(apdu)
  if r.sw1 == 0x6c:
    apdu.le = r.sw2
    apdu.send_le = 1
    r = reader.send_APDU(apdu)
  if r.sw1 == 0x67:
    apdu.le = 0x00
    apdu.send_le = 1
    r = reader.send_APDU(apdu)
  print(r)
  return r

class DriverInterface(base.BaseDriverInterface):
  def __init__(self):
    super().__init__()
    self.config = {}
    self.config["trigger"] = None
    print("Using LEIA Driver")

  def init(self,scope):
    print("LEIA: initializing")
    self.f = Fuck()
    self.scope = scope
    self.reader = LEIA("/dev/ttyACM0")
    print("LEIA: OK")

  def drive(self,data_in = None):
    try:
      return self.drive_efdir(data_in)
    except Exception as ex:
      print(ex)
      return (None,None)

  def drive_efdir(self,data_in = None):
    if data_in is None:
      next_rand = [random.randint(0,255) for _ in range(16)]
    else:
      print("TLVA!")
      next_rand = data_in
    next_autn = [random.randint(0,255) for _ in range(16)]
    print("GO")
    self.reader.reset()
    print(self.reader.get_ATR())
    r = send_and_get_resp(self.reader,self.f._select_file(0x3F00))  # MASTER
    r = send_and_get_resp(self.reader,self.f._select_file(0x2F00))
    r = send_and_get_resp(self.reader,[0x00,0xB2,0x01,0x04,r.data[7]])
    r = send_and_get_resp(self.reader,self.f._select_file(aid=r.data[4:4+r.data[3]]))
    print(next_autn,next_rand)
    l = self.f._umts_auth(next_rand,next_autn)
    time.sleep(0.1)
    self.reader.set_trigger_strategy(0, point_list=[TriggerPoints.TRIG_IRQ_PUTC],delay=len(l) - 1,single=1)
    self.scope.arm()
    send_and_get_resp(self.reader,l)
    return (next_rand,next_autn)

  def close(self):
    pass
