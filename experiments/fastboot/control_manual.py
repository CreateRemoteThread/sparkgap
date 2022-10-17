#!/usr/bin/env python3

import fastboot
import time
import phywhisperer.usb as pw
phy = pw.Usb()
phy.con(program_fpga=True)

buttonState = 0
PULSEWIDTH = 55

def togglePin(in_bit):
  global buttonState
  if in_bit >= 7:
    print("error: max is d7")
    return
  buttonState = buttonState ^ (1 << in_bit)
  phy.write_reg(phy.REG_USERIO_DATA,[buttonState])

def enterFastboot():
  PIN_RST = 0
  PIN_PWR = 1
  PIN_VOL = 2
  PIN_FET = 3
  print("enterFastboot: holding down pwr/vol")
  togglePin(PIN_PWR) 
  togglePin(PIN_VOL)
  time.sleep(0.5) 
  togglePin(PIN_FET) 
  time.sleep(0.5)
  print("enterFastboot: holding rst")
  togglePin(PIN_RST)
  time.sleep(0.5)
  print("enterFastboot: releasing rst")
  togglePin(PIN_RST)
  time.sleep(5.0)
  print("enterFastboot: releasing vol")
  togglePin(PIN_VOL)
  print("enterFastboot: releasing pwr")
  togglePin(PIN_PWR)
  print("enterFastboot: you should be in fastboot...") 
 
# flashing unlock
capturemask = [0x75,0x6e,0x6c,0x6f,0x63,0x6b]
# usb descriptor
# capturemask = [0x80, 0x06, 0x01, 0x03, 0x00, 0x00,0xFE,0x0F]

def resetFPGA():
  global phy,capturemask
  phy.reset_fpga()
  phy.set_power_source("off")
  phy.write_reg(phy.REG_USERIO_PWDRIVEN,[0xFF])
  phy.write_reg(phy.REG_USERIO_DATA,[0x0])
 
packetPrinter = pw.USBSimplePrintSink(highspeed=False)

c = None
doResetAll = True
import random

print("Entering Fastboot...")
enterFastboot()
time.sleep(1.5)
phy.set_power_source("5V")
time.sleep(1.5)
c = fastboot.ClingWrap()

def prepareCapture(us_delay=700):
  phy.set_pattern(capturemask,mask=[0xFF for c in capturemask])
  phy.set_capture_size(512)
  phy.set_pattern(capturemask,mask=[0xFF for c in capturemask])
  phy.set_trigger(enable=True,delays=[us_delay],widths=[phy.ns_trigger(PULSEWIDTH)])
  phy.arm()

while True:
  cmd = input(" > ").rstrip()
  if cmd in ["lock"]:
    prepareCapture()
    ret = c.bulkTransfer(slp=delay_time,msg="oem lock")
    print(ret)
  elif cmd in ["unlock"]:
    prepareCapture()
    ret = c.bulkTransfer(slp=delay_time)
    print(ret)
  elif cmd in ["q","quit"]:
    sys.exit(0)
  else:
    print(" usage: lock | unlock | quit")

