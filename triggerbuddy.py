#!/usr/bin/env python3

import sys
import readline
import getopt
import serial

CMD_PING = b'\x01'
CMD_READ = b'\x02'
CMD_WRITE = b'\x03'
CMD_ARM = b'\x04'
CMD_DISARM = b'\x05'

PARAM_CLKEDGES = b'\x01'
PARAM_IOEDGES = b'\x02'
PARAM_NSEDGES = b'\x03'
PARAM_PULSEWIDTH = b'\x04'

RESP_ACK = b'0xAA'
RESP_NACK = b'0xFF'
def squish(b1,b2):
  return bytes( [(ord(b1) << 4) + b2] )

def edgeCount(data):
  fc = ""
  for i in range(0,len(data)):
    fc += "0"
    fc += bin(data[i])
    fc += "1"
  return fc.count("01")

class TriggerBuddy():
  def __init__(self,port="/dev/ttyUSB1"):
    self.ser = serial.Serial(port,115200)
    # self.ser.write(CMD_PING)
    # b = self.ser.read(1)
    # if b != b'\xAA':
    #   print("TriggerBuddy: CMD_PING failed, inconsistent state detected")
    #   self.ser.close()
    #   sys.exit(0)

  def readIoEdges(self):
    a = 0
    self.ser.write(CMD_READ + PARAM_IOEDGES + b'\x00')
    a += ord(self.ser.read(1))
    self.ser.write(CMD_READ + PARAM_IOEDGES + b'\x01')
    a += ord(self.ser.read(1)) * 0x100
    self.ser.write(CMD_READ + PARAM_IOEDGES + b'\x02')
    a += ord(self.ser.read(1)) * 0x10000
    self.ser.write(CMD_READ + PARAM_IOEDGES + b'\x03')
    a += ord(self.ser.read(1)) * 0x1000000
    return a

  def readPulseWidth(self):
    a = 0
    self.ser.write(CMD_READ + PARAM_PULSEWIDTH + b'\x00')
    a += ord(self.ser.read(1))
    self.ser.write(CMD_READ + PARAM_PULSEWIDTH + b'\x01')
    a += ord(self.ser.read(1)) * 0x100
    self.ser.write(CMD_READ + PARAM_PULSEWIDTH + b'\x02')
    a += ord(self.ser.read(1)) * 0x10000
    self.ser.write(CMD_READ + PARAM_PULSEWIDTH + b'\x03')
    a += ord(self.ser.read(1)) * 0x1000000
    return a

  def readNsEdges(self):
    a = 0
    self.ser.write(CMD_READ + PARAM_NSEDGES + b'\x00')
    a += ord(self.ser.read(1))
    self.ser.write(CMD_READ + PARAM_NSEDGES + b'\x01')
    a += ord(self.ser.read(1)) * 0x100
    self.ser.write(CMD_READ + PARAM_NSEDGES + b'\x02')
    a += ord(self.ser.read(1)) * 0x10000
    self.ser.write(CMD_READ + PARAM_NSEDGES + b'\x03')
    a += ord(self.ser.read(1)) * 0x1000000
    return a

  def readClkEdges(self):
    a = 0
    self.ser.write(CMD_READ + PARAM_CLKEDGES + b'\x00')
    a += ord(self.ser.read(1))
    self.ser.write(CMD_READ + PARAM_CLKEDGES + b'\x01')
    a += ord(self.ser.read(1)) * 0x100
    self.ser.write(CMD_READ + PARAM_CLKEDGES + b'\x02')
    a += ord(self.ser.read(1)) * 0x10000
    self.ser.write(CMD_READ + PARAM_CLKEDGES + b'\x03')
    a += ord(self.ser.read(1)) * 0x1000000
    return a

  def writePulseWidth(self,value):
    self.ser.write(CMD_WRITE + squish(PARAM_PULSEWIDTH,0) + bytes( [value & 0xFF ]))
    self.ser.read(1)
    self.ser.write(CMD_WRITE + squish(PARAM_PULSEWIDTH,1) + bytes( [(value >> 8) & 0xFF]))
    self.ser.read(1)
    self.ser.write(CMD_WRITE + squish(PARAM_PULSEWIDTH,2) + bytes( [(value >> 16) & 0xFF]))
    self.ser.read(1)
    self.ser.write(CMD_WRITE + squish(PARAM_PULSEWIDTH,3) + bytes( [(value >> 24) & 0xFF]))
    self.ser.read(1)

  def writeNsEdges(self,value):
    self.ser.write(CMD_WRITE + squish(PARAM_NSEDGES,0) + bytes( [value & 0xFF ]))
    self.ser.read(1)
    self.ser.write(CMD_WRITE + squish(PARAM_NSEDGES,1) + bytes( [(value >> 8) & 0xFF]))
    self.ser.read(1)
    self.ser.write(CMD_WRITE + squish(PARAM_NSEDGES,2) + bytes( [(value >> 16) & 0xFF]))
    self.ser.read(1)
    self.ser.write(CMD_WRITE + squish(PARAM_NSEDGES,3) + bytes( [(value >> 24) & 0xFF]))
    self.ser.read(1)


  def writeIoEdges(self,value):
    self.ser.write(CMD_WRITE + squish(PARAM_IOEDGES,0) + bytes( [value & 0xFF ]))
    self.ser.read(1)
    self.ser.write(CMD_WRITE + squish(PARAM_IOEDGES,1) + bytes( [(value >> 8) & 0xFF]))
    self.ser.read(1)
    self.ser.write(CMD_WRITE + squish(PARAM_IOEDGES,2) + bytes( [(value >> 16) & 0xFF]))
    self.ser.read(1)
    self.ser.write(CMD_WRITE + squish(PARAM_IOEDGES,3) + bytes( [(value >> 24) & 0xFF]))
    self.ser.read(1)


  def writeClkEdges(self,value):
    self.ser.write(CMD_WRITE + squish(PARAM_CLKEDGES,0) + bytes( [value & 0xFF ]))
    self.ser.read(1)
    self.ser.write(CMD_WRITE + squish(PARAM_CLKEDGES,1) + bytes( [(value >> 8) & 0xFF]))
    self.ser.read(1)
    self.ser.write(CMD_WRITE + squish(PARAM_CLKEDGES,2) + bytes( [(value >> 16) & 0xFF]))
    self.ser.read(1)
    self.ser.write(CMD_WRITE + squish(PARAM_CLKEDGES,3) + bytes( [(value >> 24) & 0xFF]))
    self.ser.read(1)

  def arm(self):
    self.ser.write(CMD_ARM)
    self.ser.read(1)

  def disarm(self):
    self.ser.write(CMD_DISARM)
    self.ser.read(1)

  def processCommand(self,cmd):
    tokens = cmd.split(" ")
    if tokens[0] == "io" and len(tokens) == 2:
      self.writeIoEdges(int(tokens[1]))
      print("Io  : %d" % self.readIoEdges())
    elif tokens[0] == "ns" and len(tokens) == 2:
      self.writeNsEdges(int(tokens[1]))
      print("Ns  : %d" % self.readNsEdges())
    elif tokens[0] == "pls" and len(tokens) == 2:
      self.writePulseWidth(int(tokens[1]))
      print("Pls : %d" % self.readPulseWidth())
    elif tokens[0] == "clk" and len(tokens) == 2:
      self.writeClkEdges(int(tokens[1]))
      print("Clk : %d" % self.readClkEdges())
    elif tokens[0] in ("arm","a"):
      print("Arming!")
      self.ser.write(CMD_ARM)
      self.ser.read(1)
    elif tokens[0] in ("disarm","d"):
      print("Disarming!")
      self.ser.write(CMD_DISARM)
      self.ser.read(1)
    elif tokens[0] in ("read","r"):
      print("Clk : %d" % self.readClkEdges())
      print("Io  : %d" % self.readIoEdges())
      print("Ns  : %d" % self.readNsEdges())
      print("Pls : %d" % self.readPulseWidth())

  def close(self):
    self.ser.close()


if __name__ == "__main__":
  if len(sys.argv) == 2:
    serialport = sys.argv[1]
  else:
    serialport = "/dev/ttyUSB1" 
 
  t = TriggerBuddy(serialport)    
  print("io <ioedges> / clk <clkedges> / a / d / r");

  print("Clk : %d" % t.readClkEdges())
  print("Io  : %d" % t.readIoEdges())
  print("Ns  : %d" % t.readNsEdges())
  print("Pls : %d" % t.readPulseWidth())

  while True:
    cmd = input(" > ").rstrip().lstrip()
    tokens = cmd.split(" ")
    if tokens[0] in ("quit","q"):
      print("Bye!")
      t.close()
      sys.exit(0)
    else:
      t.processCommand(cmd)

  t.close()
