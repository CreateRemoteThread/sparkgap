#!/usr/bin/env python3

import tkinter as tk
import numpy as np
import support.filemanager

def doMergeTraces(dataItems):
  print("doMergeTraces: starting operation...")
  for f in ["file1","file2","outfile"]:
    if f not in dataItems.keys():
      print("doMergeTraces: could not find critical parameter %s" % f)
      return
  tm_in1 = support.filemanager.TraceManager(dataItems["file1"])
  tm_in2 = support.filemanager.TraceManager(dataItems["file2"])
  if tm_in1.numPoints != tm_in2.numPoints:
    print("doMergeTraces: tm_in1.numPoints != tm_in2.numPoints")
    tm_in1.cleanup()
    tm_in2.cleanup()
    return
  try:
    totalTraces = tm_in1.traceCount + tm_in2.traceCount
  except:
    print("doMergeTraces: could not add tm_in1.traceCount and tm_in2.traceCount. Are your trace files valid?")
    tm_in1.cleanup()
    tm_in2.cleanup()
    return
  traces = np.zeros((totalTraces,tm_in1.numPoints),np.float32)
  data_in = np.zeros((totalTraces,16),np.uint8)
  data_out = np.zeros((totalTraces,16),np.uint8)
  counter = 0
  for i in range(0,tm_in1.traceCount):
    traces[counter:] = tm_in1.getSingleTrace(i)
    data_in[counter:] = tm_in1.getSingleData(i)
    data_out[counter:] = tm_in1.getSingleDataOut(i)
    counter += 1
  for i in range(0,tm_in2.traceCount):
    traces[counter:] = tm_in2.getSingleTrace(i)
    data_in[counter:] = [0xFF] * 16
    data_out[counter:] = tm_in2.getSingleDataOut(i)
    counter += 1
  print("doMergeTraces: OK, %d traces merged" % counter)
  support.filemanager.save(dataItems["outfile"],traces=traces,data=data_in,data_out=data_out)


def getTraceConfig(r_str):
  r = []
  if "," in r_str:
    tokens = r_str.split(",")
  else:
    tokens = [r_str]
  for t in tokens:
    if "-" in t:
      (t1,t2) = t.split("-")
      r += list(range(int(t1),int(t2)))
    else:
      r += [int(t)]
  return r

class DlgParameters(tk.Frame):
  def __init__(self,master=None,callback=None,dataItems=[]):
    super().__init__(master)
    self.master = master
    self.callback = callback
    self.pack()
    self.widgetItems = {}
    self.dataItems = dataItems
    self.create_widgets()

  def taskCallback(self):
    if self.callback is None:
      print("uihelper.DlgParameters: skipping uninitialized callback")
      return
    tempDataObject = {}
    for f in self.dataItems:
      tempDataObject[f] = self.widgetItems["txt_%s" % f].get()
    self.callback(tempDataObject)
    self.master.destroy()

  def create_widgets(self):
    for f in self.dataItems:
      tempFrame = tk.Frame(self.master)
      self.widgetItems["frame_%s" % f] = tempFrame
      self.widgetItems["lbl_%s" % f] = tk.Label(tempFrame,text="%s" % f)
      self.widgetItems["lbl_%s" % f].pack(side=tk.LEFT)
      self.widgetItems["txt_%s" % f] = tk.Entry(tempFrame,width=20)
      self.widgetItems["txt_%s" % f].pack(side=tk.RIGHT)
      tempFrame.pack(side=tk.TOP,expand=True,fill=tk.X)
    finalFrame = tk.Frame(self.master)
    testButton = tk.Button(finalFrame,text = "OK", command=self.taskCallback)
    testButton.pack(side=tk.LEFT,expand=True,fill=tk.X)
    finalFrame.pack(side=tk.TOP,expand=True,fill=tk.X)


class DlgMergeFiles(DlgParameters):
  def __init__(self,master=None,callback=None,dataItems=[]):
    super().__init__(master,callback,dataItems)

  def grabFile(self,f):
    self.widgetItems["txt_%s" % f].delete(0,"end")
    t = tk.filedialog.askopenfilename(initialdir="~/",title="Select trace...",filetypes=(("Trace File","*.traces"),))
    self.widgetItems["txt_%s" % f].insert(0,t)

  def saveFile(self,f):
    self.widgetItems["txt_%s" % f].delete(0,"end")
    t = tk.filedialog.asksaveasfilename(initialdir="~/",title="Save output trace...",filetypes=(("Trace File","*.traces"),))
    self.widgetItems["txt_%s" % f].insert(0,t)
  
  def create_widgets(self):
    for f in self.dataItems:
      tempFrame = tk.Frame(self.master)
      self.widgetItems["frame_%s" % f] = tempFrame
      self.widgetItems["lbl_%s" % f] = tk.Label(tempFrame,text="%s" % f)
      self.widgetItems["lbl_%s" % f].pack(side=tk.LEFT)
      self.widgetItems["txt_%s" % f] = tk.Entry(tempFrame,width=20)
      if "outfile" in f:  # dirty hack to stop f from evaluating (i.e. to stop every lambda calling with "outfile")
        self.widgetItems["lambda_%s" % f] = lambda q=f: self.saveFile(q)
        self.widgetItems["btn_%s" % f] = tk.Button(tempFrame,text="...",command=self.widgetItems["lambda_%s" % f])
        self.widgetItems["btn_%s" % f].pack(side=tk.RIGHT)
      elif "file" in f:
        self.widgetItems["lambda_%s" % f] = lambda q=f: self.grabFile(q)
        self.widgetItems["btn_%s" % f] = tk.Button(tempFrame,text="...",command=self.widgetItems["lambda_%s" % f])
        self.widgetItems["btn_%s" % f].pack(side=tk.RIGHT)
      self.widgetItems["txt_%s" % f].pack(side=tk.RIGHT)
      tempFrame.pack(side=tk.TOP,expand=True,fill=tk.X)
    finalFrame = tk.Frame(self.master)
    testButton = tk.Button(finalFrame,text = "OK", command=self.taskCallback)
    testButton.pack(side=tk.LEFT,expand=True,fill=tk.X)
    finalFrame.pack(side=tk.TOP,expand=True,fill=tk.X)

class DlgPass(tk.Frame):
  def __init__(self,master=None,callback=None,dataItems=[]):
    super().__init__(master)
    self.master = master
    self.callback = callback
    self.pack()
    self.widgetItems = {}
    self.dataItems = dataItems
    self.create_widgets()

