#!/usr/bin/env python3

import usb.core
import usb.util

def sendUnlock(flashunlock=False):
  try:
    dev = usb.core.find(idVendor=0x1f3a,idProduct=0x1010)
    dev.set_configuration()
  except:
    print("sendUnlock: endpoint not found")
    return False
  cfg = dev.get_active_configuration()
  intf = cfg[(0,0)]
  ep = usb.util.find_descriptor(intf, custom_match = \
      lambda e: \
        usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT)
  assert ep is not None
  ep2 = usb.util.find_descriptor(intf, custom_match = \
      lambda e: \
        usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN)
  assert ep2 is not None
  if flashunlock:
    ep.write("flashing unlock_critical")
  else:
    ep.write("oem unlock")
  data = ep2.read(0x100)
  print("GREPTHIS: " + "".join([chr(x) for x in data]))
  # ep.close()
  # ep2.close()
  # dev.close()
  return data

if __name__ == "__main__":
  print("Sending Unlock")
  data = sendUnlock()
  if data is False:
    print("Device not connected")
  else:
    print("Data acquired")
