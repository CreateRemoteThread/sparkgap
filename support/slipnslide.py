#!/usr/bin/env python3

from numpy import *
import matplotlib as mpl
import matplotlib.pyplot as plt

def getSingleSAD(array1,array2):
  totalSAD = 0.0
  return sum(abs(array1 - array2))

class SliceEngine:
  def __init__(self, tracemanager):
    print("Creating SliceEngine...")
    self.tm_in = tracemanager

  def PrepareTemplate(self,ref_num,ref_offset, ref_length,dist_between_slices,sad_cutoff):
    wiggleRoom = 5
    print("PrepareTemplate called : ")
    print(" - ref: %d[%d:%d]" % (ref_num,ref_offset,ref_offset + ref_length))
    print(" - dist: %d" % dist_between_slices)
    print(" - sad_cutoff: %f" % sad_cutoff)
    rt = self.tm_in.getSingleTrace(ref_num)
    self.refSlice = rt[ref_offset:ref_offset + ref_length]
    print("Seeking from midpoint:")
    foundSlices = []
    for seekAttempt in range(-50,0):
      seekOffset = ref_offset + seekAttempt * dist_between_slices
      minSAD = sad_cutoff
      minShift = None
      for offset in range(-wiggleRoom, wiggleRoom):
        tempSlice = rt[seekOffset + offset:seekOffset + offset + ref_length]
        currentSAD = getSingleSAD(self.refSlice,tempSlice)
        print("Minimum SAD: ",currentSAD)
        if currentSAD < minSAD:
          minSAD = currentSAD
          minShift = offset
      if minShift != None:  # always the left edge of the block
        foundSlices.append( (minSAD,minShift) )
    print("Autoslicing complete, the following slices were found")
    print(foundSlices)
