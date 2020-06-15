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

  def FindSlices(self,ref_num,ref_offset, ref_length,dist_between_slices,sad_cutoff,maxSlicesBackwards,maxSlicesForwards):
    wiggleRoom = 15
    print("PrepareTemplate called : ")
    print(" - ref: %d[%d:%d]" % (ref_num,ref_offset,ref_offset + ref_length))
    print(" - dist: %d" % dist_between_slices)
    print(" - sad_cutoff: %f" % sad_cutoff)
    rt = self.tm_in.getSingleTrace(ref_num)
    refSlice = rt[ref_offset:ref_offset + ref_length]
    print("Seeking from midpoint:")
    foundSlices = []
    seekAdjust = 0
    for seekAttempt in range(-1,-maxSlicesBackwards,-1):
      seekOffset = seekAdjust + ref_offset + seekAttempt * dist_between_slices
      firstSAD = None
      minSAD = sad_cutoff
      minShift = None
      for offset in range(-wiggleRoom, wiggleRoom):
        tempSlice = rt[seekOffset + offset:seekOffset + offset + ref_length]
        if(seekOffset + offset < 0):
          continue
        elif seekOffset + offset + ref_length > self.tm_in.numPoints:
          continue
        currentSAD = getSingleSAD(refSlice,tempSlice)
        if firstSAD is None:
          firstSAD = currentSAD
        if currentSAD < minSAD:
          minSAD = currentSAD
          minShift = offset
      if minShift != None:  # always the left edge of the block
        seekAdjust = minShift
        foundSlices.append( (firstSAD,minSAD,minShift,seekOffset + minShift) )
    print(foundSlices)
