#!/usr/bin/env python3

from testusb import GoodFETMAXUSBHost

client = GoodFETMAXUSBHost()
client.serInit(port="/dev/ttyUSB0")

print("OK")

# client.msp430_reset(0)
# client.msp430_reset(1)
