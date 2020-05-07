#!/usr/bin/env python3

import pylink
import time

jlink = pylink.JLink()
jlink.open()
r = jlink.connect("Cortex-M3",verbose=True)
print(r)
time.sleep(5.0)
jlink.close()
