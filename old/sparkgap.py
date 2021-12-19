#!/usr/bin/env python3

import sys
import tkinter as tk
import matplotlib as mpl
mpl.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import support.filemanager
import support.uihelper
import support.sighelper
import numpy as np
import time

def doMergeTraces(dataItems):
  print("doMergeTraces: starting operation...")
  for f in ["file1","file2","outfile"]:
    if f not in dataItems.keys():
      print("doMergeTraces: could not find critical parameter %s" % f)
      return
    if len(dataItems[f]) == 0:
      print("doMergeTraces: data input '%s' was not filled in" % f)
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
    data_in[counter:] = tm_in2.getSingleData(i)
    data_out[counter:] = tm_in2.getSingleDataOut(i)
    counter += 1
  print("doMergeTraces: OK, %d traces merged" % counter)
  support.filemanager.save(dataItems["outfile"],traces=traces,data=data_in,data_out=data_out)

class Application(tk.Frame):
  def __init__(self,master=None):
    super().__init__(master)
    self.master = master
    self.mark = []
    self.pack()
    self.create_menu()
    self.activeTrace = None
    self.entry = {}
    self.statusText = tk.StringVar("")
    self.status = tk.Label(self.master,textvariable=self.statusText)
    self.status.pack(side=tk.BOTTOM,fill=tk.X,expand=True)
    self.createNavbar()
    self.create_widgets()
    self.SignalHelper = support.sighelper.SignalHelper
    self.lastTime = 0.0
    self.lastX = 0

  def dlgMergeNumpy(self):
    self.saved_dlgMergeTraces = support.uihelper.DlgMergeNumpy(tk.Toplevel(self.master),callback=support.uihelper.doMergeNumpy,dataItems=["file_pt","file_ct","file_traces","outfile"])

  def dlgMergeTraces(self):
    self.saved_dlgMergeTraces = support.uihelper.DlgMergeFiles(tk.Toplevel(self.master),callback=support.uihelper.doMergeTraces,dataItems=["file1","file2","outfile"])

  def canvasClick(self,event):
    t = time.time()
    if t - self.lastTime < 0.200:
      print("canvasClick: please click slower :)")
      return
    elif event.xdata is None:
      return
    if self.activeTrace is None:
      print("canvasClick: no trace loaded, skipping")
      return
    self.lastTime = t
    if self.lastX == 0:
      self.lastX = int(event.xdata)
      self.lastX += self.getViewOffset()
      self.mark = [self.lastX]
      self.statusText.set("MARK: %d" % self.lastX)
    else:
      localX = int(event.xdata)
      localX += self.getViewOffset()
      fromX = min(self.lastX,localX)
      toX = max(self.lastX,localX)
      dist = toX - fromX
      self.statusText.set("FROM: %d TO: %d, DIST: %d" % (fromX,toX,dist))
      self.lastX = localX
      self.mark = [toX,fromX]
    self.redrawTrace()
    return

  def getViewOffset(self):
    if self.activeTrace is None:
      return None
    try:
      return int(self.entry["txtOffset"].get())
    except:
      return None

  def selectTrace(self):
    traceSelection = self.entry["txtTraceSelect"].get()
    try:
      return support.uihelper.getTraceConfig(traceSelection)
    except:
      print("selectTrace / support.uihelper.getTraceConfig exception")
      return None

  def open_trace(self):
    fn = tk.filedialog.askopenfilename(initialdir="~/",title="Select trace...",filetypes=(("Trace File","*.traces"),))
    if len(fn) == 0:
      print("open_trace.askopenfilename returned none, user cancelled")
      return
    self.activeTrace = support.filemanager.TraceManager(fn)
    self.entry["txtTraceSelect"].delete(0,"end")
    self.entry["txtTraceSelect"].insert(0,"0")
    self.entry["txtOffset"].delete(0,"end")
    self.entry["txtOffset"].insert(0,"0")
    self.entry["txtSamplecount"].delete(0,"end")
    self.entry["txtSamplecount"].insert(0,"%d" % self.activeTrace.numPoints)
    self.redrawTrace()

  def close_trace(self):
    self.lastX = 0 # Reset mark
    self.mark = []
    if self.activeTrace is None:
      print("No active trace, nothing to do")
      return
    print("Closing active trace...")
    self.activeTrace.cleanup()
    self.activeTrace = None
    self.entry["txtTraceSelect"].delete(0,"end")
    self.entry["txtOffset"].delete(0,"end")
    self.entry["txtSamplecount"].delete(0,"end")
    self.redrawTrace()

  def redrawTrace(self):
    self.mainPlot.clear()
    if self.activeTrace is None:
      print("redrawTrace called with no active trace, open a trace first")
    else:
      try:
        # viewSelect = int(self.entry["txtTraceSelect"].get())
        viewSelect = self.selectTrace()
        viewOffset = int(self.entry["txtOffset"].get())
        viewSamplecount = int(self.entry["txtSamplecount"].get())    
      except:
        print("redrawTrace Exception: Are your inputs all base10 integers?")
        return
      if viewSelect is None:
        print("redrawTrace: viewSelect returned None, don't know what to draw")
        return
      for f in viewSelect:
        self.mainPlot.plot(self.activeTrace.getSingleTrace(f)[viewOffset:viewOffset + viewSamplecount])
      for f in self.mark:
        self.mainPlot.axvline(x = f,color='r')
    self.canvas.draw()

  def save_cw(self):
    if self.activeTrace is None:
      print("save_cw: activeTrace is None")
      return
    self.activeTrace.save_cw()

  def create_menu(self):
    self.menubar = tk.Menu(self.master)
    filemenu = tk.Menu(self.menubar,tearoff=0)
    filemenu.add_command(label="Open Trace",command=self.open_trace)
    filemenu.add_command(label="Close Trace",command=self.close_trace)
    filemenu.add_separator()
    filemenu.add_command(label="Save (CW)",command=self.save_cw)
    filemenu.add_separator()
    filemenu.add_command(label="Exit",command=self.exit_program)
    self.menubar.add_cascade(label="File",menu=filemenu)
    utilmenu = tk.Menu(self.menubar,tearoff=0)
    utilmenu.add_command(label="Merge Sparkgap Traces",command=self.dlgMergeTraces)
    utilmenu.add_command(label="Merge Numpy Traces",command=self.dlgMergeNumpy)
    # mathmenu = tk.Menu(self.menubar,tearoff=0)
    # mathmenu.add_command(label="Display FFT",command=self.dlgFFT)
    
    # self.menubar.add_cascade(label="Analysis",menu=mathmenu)
    self.menubar.add_cascade(label="Utility",menu=utilmenu)
    self.master.config(menu=self.menubar)

  def exit_program(self):
    self.close_trace()
    print("exit_program: Cleanup OK")
    sys.exit(0)
  
  def create_widgets(self):
    self.f = Figure(figsize=(8,6),dpi=100)
    self.mainPlot = self.f.add_subplot(111)
    self.canvas = FigureCanvasTkAgg(self.f,self.master)
    self.canvas.mpl_connect("button_press_event",self.canvasClick)
    self.canvas.draw()
    self.canvas_tk = self.canvas.get_tk_widget().pack(side=tk.BOTTOM,fill=tk.BOTH,expand=True)

  def lastTrace(self):
    if self.activeTrace is None:
      print("lastTrace called with no activeTrace")
      return
    viewSelect = self.selectTrace() # int(self.entry["txtTraceSelect"].get())
    if viewSelect is None:
      print("nextTrace: selectTrace returned None")
      return
    if len(viewSelect) != 1:
      print("nextTrace: selectTrace returned more than one item")
      return
    viewSelect = viewSelect[0]
    if viewSelect == 0:
      print("lastTrace called when current trace is 0")
      return
    self.entry["txtTraceSelect"].delete(0,"end")
    self.entry["txtTraceSelect"].insert(0,"%d" % (viewSelect - 1))
    self.redrawTrace() 

  def nextTrace(self):
    if self.activeTrace is None:
      print("nextTrace called with no activeTrace")
      return
    viewSelect = self.selectTrace() # int(self.entry["txtTraceSelect"].get())
    if viewSelect is None:
      print("nextTrace: selectTrace returned None")
      return
    if len(viewSelect) != 1:
      print("nextTrace: selectTrace returned more than one item")
      return
    viewSelect = viewSelect[0]
    if viewSelect + 1 >= self.activeTrace.getTraceCount():
      print("nextTrace called when already at maximum trace")
      return
    self.entry["txtTraceSelect"].delete(0,"end")
    self.entry["txtTraceSelect"].insert(0,"%d" % (viewSelect + 1))
    self.redrawTrace() 

  def deleteMarkers(self):
    self.mark = []
    self.redrawTrace()
 
  def createNavbar(self):
    self.navFrame = tk.Frame(self.master,height=100)
    self.entry["btnPrevTrace"] = tk.Button(self.navFrame,text="<",command=self.lastTrace)
    self.entry["btnPrevTrace"].pack(side=tk.LEFT)
    self.entry["txtTraceSelect"] = tk.Entry(self.navFrame,width=10)
    self.entry["txtTraceSelect"].pack(side=tk.LEFT)
    self.entry["btnNextTrace"] = tk.Button(self.navFrame,text=">",command=self.nextTrace)
    self.entry["btnNextTrace"].pack(side=tk.LEFT)
    lblOffset = tk.Label(self.navFrame,text="O:")
    lblOffset.pack(side=tk.LEFT)
    self.entry["txtOffset"] = tk.Entry(self.navFrame,width=10)
    self.entry["txtOffset"].pack(side=tk.LEFT)
    lblOffset = tk.Label(self.navFrame,text="N:")
    lblOffset.pack(side=tk.LEFT)
    self.entry["txtSamplecount"] = tk.Entry(self.navFrame,width=10)
    self.entry["txtSamplecount"].pack(side=tk.LEFT)
    self.entry["btnRefreshFilters"] = tk.Button(self.navFrame,text="Refresh",command=self.redrawTrace)
    self.entry["btnRefreshFilters"].pack(side=tk.LEFT)
    self.entry["btnDeleteMarkers"] = tk.Button(self.navFrame,text="Remove Marks",command=self.deleteMarkers)
    self.entry["btnDeleteMarkers"].pack(side=tk.RIGHT)
    self.navFrame.pack(side=tk.TOP,fill=tk.X,expand=True)

if __name__ == "__main__":
  root = tk.Tk()
  root.title("sparkgap.py")
  root.geometry("800x600")
  app = Application(master=root)
  app.mainloop()

