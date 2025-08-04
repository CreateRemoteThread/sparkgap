#!/usr/bin/env python3

def unpackKeeloq(plaintext):
  out = ""
  for i in range(0,9):
    out = format(plaintext[i],"08b") + out
  return out
  # return out[6:]

def packKeeloq(bitstring):
  bs = int(bitstring,2)
  out = [0] * 16
  for i in range(0,9):
    fq = (bs >> (i * 8)) & 0xFF
    out[i] = fq
  return out

def doFlipKeeloqIO(tm_in,varMgr):
  numTraces = tm_in.traceCount
  sampleCnt = tm_in.numPoints
  traces = zeros((numTraces,sampleCnt),tm_in.getDtype())
  data = zeros((numTraces,16),uint8)
  data_out = zeros((numTraces,16),uint8)
  savedDataIndex = 0
  CONFIG_WRITEFILE = varMgr.getVariable("writefile")
  for i in range(0,numTraces):
    print("Flipping IO for trace %d..." % i)
    traces[savedDataIndex,:] = tm_in.getSingleTrace(i)
    # print(unpackKeeloq(tm_in.getSingleData(i))[::-1])
    # print(packKeeloq(unpackKeeloq(tm_in.getSingleData(i))[::-1]))
    # sys.exit(0)
    data[savedDataIndex,:] = packKeeloq(unpackKeeloq(tm_in.getSingleData(i))[::-1])
    data_out[savedDataIndex,:] = packKeeloq(unpackKeeloq(tm_in.getSingleDataOut(i)[::-1])[::-1])
    savedDataIndex += 1
  print("Returning data, don't forget to commit!")
  return (traces[0:savedDataIndex],data[0:savedDataIndex],data_out[0:savedDataIndex])
  # print("Saving...")
  # sparkgap.filemanager.save(CONFIG_WRITEFILE,traces=traces[0:savedDataIndex],data=data[0:savedDataIndex],data_out=data_out[0:savedDataIndex])



