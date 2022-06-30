#!/usr/bin/env python3

# Timon, 2019
# Non Profiled Deep Learning SCA

import sys
import pandas as pd
import keras
import numpy as np
import support.filemanager
import support.attack

FN_IN = None
SAMPLE_OFFSET = None
SAMPLE_COUNT = None
CFG_ATTACK = None

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

leakmodel = support.attack.fetchModel(CFG_ATTACK)
tm = support.filemanager.TraceManager(FN_IN)

t_test = tm.getSingleTrace(0)

if SAMPLE_OFFSET is None:
  SAMPLE_OFFSET = 0

if SAMPLE_OFFSET > len(t_test):
  print("Sample offset must be within (0,%d)", % len(t_test))
  sys.exit(0)

if SAMPLE_COUNT is None:
  SAMPLE_COUNT = len(t_test) - SAMPLE_OFFSET

if SAMPLE_OFFSET + SAMPLE_COUNT > len(t_test):
  print("Sample count must be within (1,%d)", % (1,len(t_test)) )
  sys.exit(0)

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
    print(self.metrics["loss"])
    return self.metrics['loss'][-1]

  def on_epoch_end(self,epoch,logs={}):
    for metric in logs:
      if metric in self.metrics:
        self.metrics[metric].append(logs.get(metric))
      else:
        self.metrics[metric] = [logs.get(metric)]

def deriveTrainingMetric(tm,leakmodel,byteGuess):
  hyp = np.zeros(tm.traceCount,np.uint8)
  for tnum in range(0,tm.traceCount):
    hyp[tnum] = leakmodel.genIVal(tnum,0,byteGuess) >= 4
  model = tf.keras.models.Sequential()
  model.add(tf.keras.layers.Flatten())
  model.add(tf.keras.layers.Dense(256,activation="relu"))
  model.add(tf.keras.layers.Dense(32,activation="relu"))
  model.add(tf.keras.layers.Dense(9,activation="softmax"))
  model.compile(optimizer=tf.keras.optimizers.RMSprop(lr=0.001),loss="sparse_categorical_crossentropy",metrics=['accuracy'])
  globalCallback = PlotLearning()
  model.fit(tm.traces[:,SAMPLE_OFFSET:SAMPLE_OFFSET + SAMPLE_COUNT],hyp,epochs=30,batch_size=12,validation_split=0.05,callbacks=[globalCallback])
  return globalCallback.getLastAccuracy()

bguess = np.zeros(255,np.float)
for byteGuess in range(0x20,0x30):
  bguess[byteGuess] = deriveTrainingMetric(tm,leakmodel,byteGuess)

import matplotlib.pyplot as plt
plt.plot(bguess)
plt.show()

t = bguess
i = np.argmin(t[0x20:0x30])
print("Chosen key: %02x, Train_MSE: %f" % (i + 0x20,bguess[i + 0x20]))
print("Correct key: 0x2b, Train_MSE: %f" % bguess[0x2b])
