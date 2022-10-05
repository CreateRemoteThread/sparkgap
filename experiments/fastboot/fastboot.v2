#!/usr/bin/env python3

import usb.core
import usb.util

class ClingWrap:
  def __init__(self):
    dev = usb.core.find(idVendor=0x1f3a,idProduct=0x1010)
    dev.set_configuration()
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
    self.ep = ep
    self.ep2 = ep2   

  def bulkTransfer(self,msg="oem unlock"):
    self.ep.write(msg)
    data = self.ep2.read(0x100)
    print(data) 
    return data
    
if __name__ == "__main__":
  c = ClingWrap()
  print("Sending Unlock")
  print(c.bulkTransfer())
  print(c.bulkTransfer())
  
  
