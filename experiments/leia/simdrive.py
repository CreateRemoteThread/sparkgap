#!/usr/bin/env python3

# this needs custom firmware for leia to work.

import random
from smartleia import APDU,TriggerPoints,LEIA
from smartleia import create_APDU_from_bytes          # ghetto hack to end all hacks

reader = LEIA("/dev/ttyACM0")

# print(reader.get_version())
print(reader.get_mode())
reader.reset()
print("Retrieving ATR")
print(reader.get_ATR())

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

def send_and_get_resp(byte_array):
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

reader.set_trigger_strategy(0, point_list=[])

f = Fuck()
r = send_and_get_resp(f._select_file(0x3F00))   # MASTER
r = send_and_get_resp(f._select_file(0x2F00))   # EF_DIR
r = send_and_get_resp([0x00,0xB2,0x01,0x04,r.data[7]])
AID = r.data[4:4+r.data[3]]
# AID = [0] * 5
print(" ".join(["%02x" % x for x in AID]))
r = send_and_get_resp(f._select_file(aid=r.data[4:4+r.data[3]]))

# srsran/srsue end of init

next_rand = [random.randint(0,255) for _ in range(16)]
next_autn = [random.randint(0,255) for _ in range(16)]
print("OK!")

l = f._umts_auth(next_rand,next_autn)
reader.set_trigger_strategy(0, point_list=[TriggerPoints.TRIG_IRQ_PUTC],delay=len(l) - 1,single=1)
print(reader.get_trigger_strategy(0))

r = send_and_get_resp(l)
print(reader.get_trigger_strategy(0))

