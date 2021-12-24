#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
import sys
import sdr_helper

plot1 = np.fromfile(sys.argv[1],dtype=np.float)
plot2 = np.fromfile(sys.argv[2],dtype=np.float)
ax1 = plt.subplot(2,1,1)
ax2 = plt.subplot(2,1,2)
ax1.set_title(sys.argv[1])
ax2.set_title(sys.argv[2])

ax1.plot(sdr_helper.flatten_fft(plot1))
ax2.plot(sdr_helper.flatten_fft(plot2))

plt.show()
