#!/usr/bin/env python3

from numpy import *
# import matplotlib as mpl
# import matplotlib.pyplot as plt

def getSingleSAD(array1,array2):
  totalSAD = 0.0
  return sum(abs(array1 - array2))

class SliceEngine:
  def __init__(self, tracemanager):
    print("Creating SliceEngine...")
    self.tm_in = tracemanager

  def FindSlices(self,ref_num,ref_offset, ref_length,dist_between_slices,sad_cutoff,maxSlicesBackwards,maxSlicesForwards):
    wiggleRoom = 15
    print("PrepareTemplate called : ")
    print(" - ref: %d[%d:%d]" % (ref_num,ref_offset,ref_offset + ref_length))
    print(" - dist: %d" % dist_between_slices)
    print(" - sad_cutoff: %f" % sad_cutoff)
    rt = self.tm_in.getSingleTrace(ref_num)
    refSlice = rt[ref_offset:ref_offset + ref_length]
    traceAverage = average(refSlice)
    print("Seeking from midpoint:")
    foundSlices = array([])
    seekAdjust = 0
    seekOffset = ref_offset
    x = []
    for i in range(-maxSlicesBackwards,maxSlicesForwards):
      minSAD = None
      minTest = None
      minAdjust = None
      if i == 0:
        seekOffset = ref_offset
      elif i < 0:
        seekOffset -= ref_length
      elif i > 0:
        seekOffset += ref_length
      if seekOffset - (ref_length // 4) <= 0 or seekOffset + ref_length + (ref_length // 4) - 1 >= self.tm_in.numPoints:
        print("Stop at sample 0, i is %d" % i)
        x = append(x,[traceAverage] * ref_length)
        x = append(x,[0,0,0])
        continue
      for seekAttempt in range(-ref_length // 4, ref_length // 4):
        currentTest = seekOffset + seekAttempt
        currentSAD = getSingleSAD(refSlice,rt[currentTest:currentTest + ref_length])
        if minSAD is None or currentSAD < minSAD:
          minSAD = currentSAD
          minTest = currentTest
          minAdjust = seekAttempt
      seekOffset = minTest
      print("Minimal SAD,Minimal Adjust: %f,%d" % (minSAD,minAdjust))
      x = append(x,rt[seekOffset:seekOffset + ref_length])
      x = append(x, [0,0,0])
      #plt.plot(rt[seekOffset:seekOffset + ref_length])
    # plt.plot(x)
    # plt.show()
    return x
