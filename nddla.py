#!/usr/bin/env python3

# Timon, 2019
# Non Profiled Deep Learning SCA

import getopt
import sys
import pandas as pd
import keras
import numpy as np
import sparkgap.filemanager
import sparkgap.attack
import platform

FN_IN = None
SAMPLE_OFFSET = None
SAMPLE_COUNT = None
CFG_ATTACK = None

BYTENUM_MIN = 0
BYTENUM_MAX = 1
KEYBYTE_MIN = 0x28
KEYBYTE_MAX = 0x30

if __name__ == "__main__":
  opts, args = getopt.getopt(sys.argv[1:],"f:o:n:a:",["file=","offset=","numsamples=","attack="])
  for opt,val in opts:
    if opt in ["-f","--file"]:
      FN_IN = val
    elif opt in ["-a","--attack"]:
      CFG_ATTACK = val
    elif opt in ["-o","--offset"]:
      SAMPLE_OFFSET = int(val)
    elif opt in ["-n","--numsamples"]:
      SAMPLE_COUNT = int(val)

if FN_IN is None:
  print("You must specify a filename with -f")
  sys.exit(0)

if CFG_ATTACK is None:
  print("You must specify an attack model with -a")
  sys.exit(0)

leakmodel = sparkgap.attack.fetchModel(CFG_ATTACK)
tm = sparkgap.filemanager.TraceManager(FN_IN)

t_test = tm.getSingleTrace(0)

if SAMPLE_OFFSET is None:
  SAMPLE_OFFSET = 0

if SAMPLE_OFFSET > len(t_test):
  print("Sample offset must be within (0,%d)" % len(t_test))
  sys.exit(0)

if SAMPLE_COUNT is None:
  SAMPLE_COUNT = len(t_test) - SAMPLE_OFFSET

if SAMPLE_OFFSET + SAMPLE_COUNT > len(t_test):
  print("Sample count must be within (1,%d)" % (len(t_test)) )
  sys.exit(0)

# snip snip
tm.cutTraces(SAMPLE_OFFSET,SAMPLE_OFFSET + SAMPLE_COUNT)

leakmodel.loadPlaintextArray(tm.loadPlaintexts())

from sklearn.linear_model import LinearRegression
from sklearn import metrics
from sklearn.metrics import mean_squared_error

import tensorflow as tf

class PlotLearning(tf.keras.callbacks.Callback):
  def on_train_begin(self,logs={}):
    self.metrics = {}
    for metric in logs:
      self.metrics[metric] = []

  def getLastAccuracy(self):
    return (self.metrics['loss'],self.metrics['accuracy'])

  def on_epoch_end(self,epoch,logs={}):
    for metric in logs:
      if metric in self.metrics:
        self.metrics[metric].append(logs.get(metric))
      else:
        self.metrics[metric] = [logs.get(metric)]

def deriveTrainingMetric(tm,leakmodel,roundNum,byteGuess):
  hyp = np.zeros(tm.traceCount,np.uint8)
  for tnum in range(0,tm.traceCount):
    hyp[tnum] = leakmodel.genIVal(tnum,roundNum,byteGuess) >= 4
  model = tf.keras.models.Sequential()
  model.add(tf.keras.layers.Flatten())
  model.add(tf.keras.layers.Normalization())
  model.add(tf.keras.layers.Dense(256,activation="relu"))
  model.add(tf.keras.layers.Dense(32,activation="relu"))
  model.add(tf.keras.layers.Dense(9,activation="softmax"))
  if platform.system() == "Darwin":
    model.compile(optimizer=tf.keras.optimizers.legacy.RMSprop(lr=0.001),loss="sparse_categorical_crossentropy",metrics=['accuracy'])
    # see https://developer.apple.com/forums/thread/721619
  else:
    model.compile(optimizer=tf.keras.optimizers.RMSprop(lr=0.001),loss="sparse_categorical_crossentropy",metrics=['accuracy'])
  globalCallback = PlotLearning()
  model.fit(tm.traces,hyp,epochs=30,batch_size=12,validation_split=0.05,callbacks=[globalCallback])
  return globalCallback.getLastAccuracy()

import matplotlib.pyplot as plt

outKey = [0] * 16

fig,(ax1,ax2) = plt.subplots(2,1)

bguess = [[]   ] * 255
bguess_last = [1.0] * 255
aguess = [ [] ] * 255
acc_last = [0.0] * 255
for roundNum in range(BYTENUM_MIN,BYTENUM_MAX):
  # bguess = np.full(255,1.0,dtype=np.float)
  for byteGuess in range(KEYBYTE_MIN,KEYBYTE_MAX):
    print(" --> Evaluating key: %02x <--" % byteGuess)
    (lastLoss,lastAcc) = deriveTrainingMetric(tm,leakmodel,roundNum,byteGuess)
    bguess[byteGuess] = lastLoss
    aguess[byteGuess] = lastAcc
    bguess_last[byteGuess] = bguess[byteGuess][-1]
    acc_last[byteGuess] = lastAcc[-1]   # don't need to plot this.
    i = np.argmin(bguess_last[KEYBYTE_MIN:KEYBYTE_MAX])
    i_acc = np.argmax(acc_last[KEYBYTE_MIN:KEYBYTE_MAX])
    print("Round %d, Chosen key: %02x, Chosen key acc: %02x, Train_MSE: %f" % (roundNum,i + KEYBYTE_MIN,i_acc+KEYBYTE_MIN,bguess_last[i + KEYBYTE_MIN]))
    outKey[roundNum] = i + KEYBYTE_MIN
  ax1.set_title("Training Loss vs Time")
  for x in range(KEYBYTE_MIN,KEYBYTE_MAX):
    if x == i:
      ax1.plot(bguess[x],color="red")
      # ax2.plot(aguess[x],color="red")
    elif x == i_acc:
      ax1.plot(bguess[x],color="blue")
      # ax2.plot(aguess[x],color="blue")
    else:
      ax1.plot(bguess[x],color="grey")
      # ax2.plot(aguess[x],color="grey")
  ax2.set_title("Last Loss (Red) / Last Acc (Blue)  vs Character")
  ax2.plot(bguess_last,color="red")
  ax3 = ax2.twinx()
  ax3.plot(acc_last,color="blue")
  plt.show()   # todo: smarter plotting (to png?)

print("=" * 80)
print("Final key: ")
print(" ".join( ["%02x" % outKey[i] for i in range(0,16)]  ))
print("=" * 80)

plt.show()

