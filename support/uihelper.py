#!/usr/bin/env python3

import tkinter as tk

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
      self.widgetItems["txt_%s" % f].pack(side=tk.LEFT)
      tempFrame.pack(side=tk.TOP)
    finalFrame = tk.Frame(self.master)
    testButton = tk.Button(finalFrame,text = "OK", command=self.taskCallback)
    testButton.pack(side=tk.LEFT,expand=True,fill=tk.X)
    finalFrame.pack(side=tk.TOP,expand=True,fill=tk.X)
     
