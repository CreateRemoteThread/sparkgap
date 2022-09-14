#!/usr/bin/env python3

from drivers import base
# import random
import time
import random
import serial

SELECT_NONE = 0x0
SELECT_MOSFET = 0x01
SELECT_MUXA = 0x02
SELECT_MUXB = 0x04
SELECT_MUXC = 0x08

def splitDword(inval):
    d0 = inval & 0xFF
    d1 = (inval >> 8) & 0xFF
    d2 = (inval >> 16) & 0xFF
    d3 = (inval >> 24) & 0xFF
    return (d3,d2,d1,d0)

class Glitcher:
    def __init__(self):
        self.u1 = serial.Serial("/dev/ttyUSB0",115200)
        # self.u1 = UART(0, baudrate=115200)
        # self.en = Pin(2,Pin.OUT)
        # self.en.value(1)
        time.sleep(0.1)
        # self.u1.read()
        print("OK")

    def setrepeat(self,num=0,delay=0):
        self.u1.write(bytes([0x03,0x30,delay & 0xFF]))  # delay
        self.u1.write(bytes([0x03,0x31,(delay >> 8) & 0xFF]))
        self.u1.write(bytes([0x03,0x32,num & 0xFF]))
        self.u1.write(bytes([0x03,0x33,(num >> 8) & 0xFF]))
        time.sleep(0.1)
        self.u1.read()

    # 0x1 = glitcher
    # 0xF = x mux
    def setmask(self,muxnum=1):
        self.u1.write(bytes([0x03,0x50,muxnum]))
        time.sleep(0.1)
        print(self.u1.read())
        self.disarm()
        
    # manual mux out
    def muxout(self,muxnum=0):
        self.u1.write(bytes([0x03,0x60,muxnum]))
        time.sleep(0.1)
        print(self.u1.read())
        self.disarm()
        
    def glitchLoop(self,delay=None,width=None,count=50):
        delayMin = 5
        delayMax = 50
        widthMin = 5
        widthMax = 10
        if delay is not None:
            (delayMin,delayMax) = delay
        if width is not None:
            (widthMin,widthMax) = width
        for i in range(0,count):
            rdelay = random.randint(delayMin,delayMax)
            rwidth = random.randint(widthMin,widthMax)
            print("Attempt %d (d:%d, w:%d)" % (i,rdelay,rwidth))
            self.rnr(delay=rdelay,width=rwidth)
            time.sleep(0.25)
            r = self.check(verbose=False) 
            while ((r != 0) and (r != 4)):
                time.sleep(0.1)
                r = self.check(verbose=False)  
    
    def check(self,verbose=False):
        self.u1.write(b"\x06")
        time.sleep(0.1)
        d = self.u1.read(1)
        if verbose is True:
            print(d)
        return int(d[0])
    
    def arm(self):
        self.u1.write(b"\x04")
        time.sleep(0.1)
        d = self.u1.read(1)
        print(d)
    
    def disarm(self):
        self.u1.write(b"\x05")
        time.sleep(0.1)
        d = self.u1.read(1)
        print(d)

    def rnr(self,delay=None,width=None,verbose=False):
        self.u1.write(b"\x05")
        if delay is None:
            delay = random.randint(5,10)
        (d3,d2,d1,d0) = splitDword(delay)
        self.u1.write(bytes([0x03,0x10,d0]))  # delay
        self.u1.write(bytes([0x03,0x11,d1]))
        self.u1.write(bytes([0x03,0x12,d2]))
        self.u1.write(bytes([0x03,0x13,d3]))
        if width is None:
            width = random.randint(5,10)
        (w3,w2,w1,w0) = splitDword(width)
        self.u1.write(bytes([0x03,0x40,w0]))  # width
        self.u1.write(bytes([0x03,0x41,w1]))
        self.u1.write(bytes([0x03,0x42,w2]))
        self.u1.write(bytes([0x03,0x43,w3]))
        self.u1.write(b"\x04")
        time.sleep(0.1)
        d = self.u1.read()
        if verbose:
            print(d)
        
    def ping(self):
        self.u1.write(bytes([0x01]))
        time.sleep(0.1)
        print(self.u1.read(1))

class DriverInterface(base.BaseDriverInterface):
  def __init__(self):
    super().__init__()
    self.config = {}
    self.config["trigger"] = None
    print("Using glitcher_pwr driver")
    self.g = Glitcher()
    self.g.muxout(0)

  def init(self,scope):
    self.scope = scope
    print("glitcher_pwr initialization: nothing needed")
   
  def drive(self,data_in = None):
    next_rand = [1 for _ in range(16)]
    next_autn = [1 for _ in range(16)]
    self.scope.arm()
    time.sleep(0.5)
    self.g.muxout(0x2)
    time.sleep(0.5)
    self.g.muxout(0x0)
    return (next_rand,next_autn)

  def close(self):
    pass
