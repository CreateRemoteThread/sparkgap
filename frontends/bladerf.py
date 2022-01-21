#!/usr/bin/env python3

import sys
import binascii
import time

plt = None

class CaptureInterface():
  def __init__(self):
    print("=" * 80)
    print("Please confirm that you have /tmp/bladeRF set up as a RAMFS with")
    print("enough space to hold a single trace, and bladeRF-cli is present")
    print("and can see your device.")
    print("")
    print("Enter 'YES' to continue")
    print("=" * 80)
    x = input().strip()
    if x != "YES":
      print("FATAL: User did not confirm setup, exiting")
      sys.exit(0)
    print("bladerf: Using experimental bladeRF frontend")
    self.config = {}

  def init(self):
    print("bladerf: todo - for now, copy the file yourself")

  def arm(self):
    

  def capture(self):
    

  def close(self):
    os.system("rm /tmp/bladeRF/*")
