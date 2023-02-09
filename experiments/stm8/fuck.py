#!/usr/bin/env python3

import os
import os.path
import serial
import random
ser = serial.Serial("/dev/ttyACM0",9600,timeout=0.5)
for i in range(0,500):
  r_delay = random.randint(720,770)
  r_width = random.randint(5,7)
  r_reps = random.randint(1,4)
  r_rdelay = random.randint(6,10)
  ser.write(b"g.setrepeat(num=%d,delay=%d)\r" % (r_reps,r_rdelay))
  ser.write(b"g.rnr(delay=%d,width=%d)\r" % (r_delay,r_width))
  d = ser.read(128)
  os.system("rm /tmp/poo.bin")
  os.system("./stm8flash -p stm8l101k3 -c stlinkv2 -r /tmp/poo.bin")
  os.system("xxd /tmp/poo.bin | head -n20")
  os.system("md5sum /tmp/poo.bin")
  if os.path.isfile("/tmp/poo.bin"):
    print("Attempt: Success (%d, %d, %d, %d)" % (r_delay,r_width,r_reps,r_rdelay))
    f = open("/tmp/poo.bin","rb")
    c = f.read(1)
    if c[0] != 0x71:
      print("what?!")
      import out
      sys.exit(0)
    f.close()
  else:
    print("Attempt: Failure (%d, %d, %d, %d)" % (r_delay,r_width,r_reps,r_rdelay))
