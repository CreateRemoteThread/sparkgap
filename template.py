#!/usr/bin/env python3

import sys
import getopt
import sparkgap.filemanager
import sparkgap.attack
import numpy as np
import matplotlib.pyplot as plt

def generateTemplate(tm_in,model,attackByte=1):
  model.loadPlaintextArray(tm_in.loadPlaintexts())
  # ciphertext is known key (uart driver with rekey opt)
  model.loadCiphertextArray(tm_in.loadCiphertexts())
  tempTracesHW = [ [] for _ in range(9) ]
  # categorize according to hw of sbox output
  for i in range(tm_in.traceCount):
    hw = model.genIVal(i,attackByte,model.ct[i,attackByte])
    tempTracesHW[hw].append(tm_in.traces[i])
  print("Trace categorisation: ")
  for i in range(0,9):
    print(" IntVal Hamming Weight %d: %d traces" % (i,len(tempTracesHW[i])))
  # find means for each hw intval
  tempMeans = np.zeros( (9,tm_in.numPoints) )
  for i in range(9):
    tempMeans[i] = np.average(tempTracesHW[i],0)
  tempSumDiff = np.zeros(tm_in.numPoints)
  sumCnt = 0
  for i in range(9):
    for j in range(i):
      sumCnt += 1
      tempSumDiff += np.abs(tempMeans[i] - tempMeans[j])
  # POI_BRACKET_MIN = 0
  # POI_BRACKET_MAX = 15000
  # tempSumDiff = tempSumDiff[POI_BRACKET_MIN:POI_BRACKET_MAX]
  numPOIs = 5
  POIspacing = 5
  POIs = []
  for i in range(numPOIs):
    nextPOI = tempSumDiff.argmax()
    POIs.append(nextPOI)
    poiMin = max(0,nextPOI - POIspacing)
    poiMax = min(nextPOI + POIspacing,len(tempSumDiff))
    for j in range(poiMin,poiMax):
      tempSumDiff[j] = 0
  # print("POI's")
  # print(POIs)
  # plt.plot(tempSumDiff)
  # plt.show()
  meanMatrix = np.zeros((9,numPOIs))
  for HW in range(9):
    for i in range(numPOIs):
      meanMatrix[HW][i] = tempMeans[HW][POIs[i]]
  covMatrix = np.zeros( (9,numPOIs,numPOIs) )
  for HW in range(9):
    for i in range(numPOIs):
      for j in range(numPOIs):
        # print(POIs[i])
        x = np.array(tempTracesHW[HW])[:,POIs[i]]
        y = np.array(tempTracesHW[HW])[:,POIs[j]]
        covMatrix[HW,i,j] = np.cov(x,y)[0][1]
  return (meanMatrix,covMatrix,POIs)
  # print(meanMatrix)
  # print(covMatrix[0])

from scipy.stats import multivariate_normal

def applyTemplate(tm_in,model,meanmatrix,covmatrix,POIs,attackByte=1):
  P_k = np.zeros(256)
  model.loadPlaintextArray(tm_in.loadPlaintexts())
  model.loadCiphertextArray(tm_in.loadCiphertexts())
  for j in range(tm_in.traceCount):
    a = [tm_in.traces[j][POIs[i]] for i in range(len(POIs))]
    for k in range(256):
      hw = model.genIVal(j,attackByte,k)
      rv = multivariate_normal(meanmatrix[hw],covmatrix[hw],allow_singular=True)
      p_kj = rv.logpdf(a)
      P_k[k] += p_kj
    print(" ".join(["%02x" % j for j in P_k.argsort()[-5:]]))

def usage():
  print("template.py: manual templating attack")
  print(" -f: trace set to build template")
  print(" --holdout: trace set to apply template")
  print(" -a: specify attack model")
  sys.exit(0)

if __name__ == "__main__":
  try:
    opts, remainder = getopt.getopt(sys.argv[1:],"f:h:a:",["help","file=","holdout=","attack="])
  except:
    usage()
  tm_template = None
  tm_holdout = None
  leakmodel = None
  for opt,arg in opts:
    if opt in ("--help"):
      usage()
      sys.exit(0)
    elif opt in ("-f","--file"):
      tm_template = sparkgap.filemanager.TraceManager(arg)
    elif opt == "--holdout":
      tm_holdout = sparkgap.filemanager.TraceManager(arg)
    elif opt in ("-a","--attack"):
      leakmodel = sparkgap.attack.fetchModel(arg)
  if tm_template is None:
    print("You must specify a template dataset with -f")
    sys.exit(0)
  elif tm_holdout is None:
    print("You must specify a holdout dataset with --holdout")
    sys.exit(0)
  elif leakmodel is None:
    print("You must specify a leak model with -a")
    sys.exit(0)
  print("ok, attempting to generate template")
  (mm,cm,POIs) = generateTemplate(tm_template,leakmodel)
  applyTemplate(tm_holdout,leakmodel,mm,cm,POIs)
