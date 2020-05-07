#!/usr/bin/env python3

import support
import phywhisperer.usb as pw
import base64
import pickle
import sys
import getopt
import csv
import string

# reads classifier csv
# and feeds it into classifier core

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print("Use: ./reader.py <blah>")
    sys.exit(0)

def tryhex(char_array):
  return "".join(["%02x" % x for x in char_array])

def tryfix(char_array):
  out = ""
  for c in char_array:
    if chr(c) in string.printable:
      out += chr(c)
    else:
      out += "."
  return out

phy = pw.Usb()

c = support.ReportingCore()

f = open(sys.argv[1],"r")
spamreader = csv.reader(f,delimiter=',')
for row in spamreader:
  (delay,width,output,rawdata) = row
  output = output[2:-1]
  rawdata = rawdata[2:-1]
  q = base64.b64decode(output)
  print("%s:%s:%s" % (delay,width,base64.b64decode(output)))
  delay = float(delay)
  width = int(width)
  muteFlag = False
  data = base64.b64decode(rawdata)
  data = pickle.loads(data)
  packets=phy.split_packets(data)
  printPackets=pw.USBSimplePrintSink(highspeed=1)
  for packet in packets:
    if len(q) == 0:
      c.addResult(delay,width,status=support.Status.Mute)
      muteFlag = True
    if packet["size"] > 30 and packet["size"] < 67 and muteFlag is False:
      print(tryhex(packet["contents"]))
      print(tryfix(packet["contents"]))
      print("%f:GLITCH:%s" % (delay,tryfix(q)))
      c.addResult(delay,width,status=support.Status.Glitch)
      muteFlag = True
      # sys.exit(0)
    if packet["contents"] == [45,0,16] and muteFlag is False:
      c.addResult(delay,width,status=support.Status.Mute)
      muteFlag = True
    print(packet)
    # printPackets.handle_usb_packet(ts=packet['timestamp'],buf=bytearray(packet['contents']),flags=0)
  if base64.b64decode(output) == b'HelloHelloHelloHelloHello' and muteFlag is False:
    c.addResult(delay,width,status=support.Status.Expected)
    muteFlag = True
  if muteFlag is False:
    print("%f:GLITCH:%s" % (delay,tryfix(q)))
    c.addResult(delay,width,status=support.Status.Glitch)

c.startPlot()
