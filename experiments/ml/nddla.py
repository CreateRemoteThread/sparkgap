#!/usr/bin/env python3

# Timon, 2019
# Non Profiled Deep Learning SCA

import sys
import pandas as pd
import keras
import numpy as np
import support.filemanager
import support.attack

leakmodel = support.attack.fetchModel("AES_SboxOut_HW")
tm = support.filemanager.TraceManager(sys.argv[1])

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
  model.fit(tm.traces[:,0:8000],hyp,epochs=30,batch_size=12,validation_split=0.05,callbacks=[globalCallback])
  return globalCallback.getLastAccuracy()
  # print("+ %f" % globalCallback.getLastAccuracy())i

bguess = np.zeros(255,np.float)
for byteGuess in range(0,0xFF):
  bguess[byteGuess] = deriveTrainingMetric(tm,leakmodel,byteGuess)

import matplotlib.pyplot as plt
plt.plot(bguess)
plt.show()

t = bguess
i = np.argmin(t)
print("Chosen key: %02x, Train_MSE: %f" % (i,bguess[i]))
print("Correct key: 0x2b, Train_MSE: %f" % bguess[0x2b])
