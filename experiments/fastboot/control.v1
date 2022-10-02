#!/usr/bin/env python3

import fastboot
import time
import phywhisperer.usb as pw
phy = pw.Usb()
phy.con(program_fpga=True)

buttonState = 0


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
 
# get flashing unlock too
capturemask = [0x75,0x6e,0x6c,0x6f,0x63,0x6b]

def resetFPGA():
  global phy,capturemask
  phy.reset_fpga()
  phy.set_power_source("off")
  phy.write_reg(phy.REG_USERIO_PWDRIVEN,[0xFF])
  phy.write_reg(phy.REG_USERIO_DATA,[0x0])
 
packetPrinter = pw.USBSimplePrintSink(highspeed=False)

import random
glitchCtr = 16.83
while glitchCtr <= 16.85:
  glitchCtr += 0.0001
  # for glitchCtr in range(14.5,17.5,0.01):
  ret = ""
  print("[%f] Resetting FPGA state" % glitchCtr)
  resetFPGA()
  print("[%f] Entering (fast) attempt" % glitchCtr)
  phy.set_pattern(capturemask,mask=[0xFF for c in capturemask])
  us_delay = glitchCtr
  print("[%f] Using us_delay is %d" % (glitchCtr,us_delay))
  print("[%f] Resetting device and trying again" % glitchCtr)
  phy.set_usb_mode(mode="HS")
  enterFastboot()
  time.sleep(2.0)
  phy.set_power_source("5V")
  time.sleep(1.0)
  phy.set_capture_size(512)
  phy.set_pattern(capturemask,mask=[0xFF for c in capturemask])
  # phy.set_trigger(enable=False)
  phy.set_trigger(enable=True,delays=[phy.us_trigger(us_delay)],widths=[phy.ns_trigger(50)])
  phy.arm()
  try:
    ret = fastboot.sendUnlock(True)
  except:
    print("[%f] Hard powering off device (exception)" % glitchCtr)
    phy.set_power_source("off")
    togglePin(3) # PIN_FET
    time.sleep(1.0)
    continue
  if ret != False:
    phy.wait_disarmed()
    raw = phy.read_capture_data()
    packets = phy.split_packets(raw)
    # for packet in packets:
    #   if len(packet["contents"]) == 3 and packet["contents"][0] == 165:
    #     continue
    #   packetPrinter.handle_usb_packet(ts=packet["timestamp"],buf=bytearray(packet["contents"]),flags=0)
  print("[%f] Hard powering off device" % glitchCtr)
  phy.set_power_source("off")
  togglePin(3) # PIN_FET
  time.sleep(1.0)
