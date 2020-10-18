#!/usr/bin/env python3

import sys
import tkinter as tk
import matplotlib as mpl
mpl.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import support.filemanager

class Application(tk.Frame):
  def __init__(self,master=None):
    super().__init__(master)
    self.master = master
    self.pack()
    self.create_menu()
    self.activeTrace = None
    self.entry = {}
    self.status = tk.Label(self.master,text="")
    self.status.pack(side=tk.BOTTOM,fill=tk.X,expand=True)
    self.createNavbar()
    self.create_widgets()

  def open_trace(self):
    fn = tk.filedialog.askopenfilename(initialdir="~/",title="Select trace...",filetypes=(("Trace File","*.traces"),))
    self.activeTrace = support.filemanager.TraceManager(fn)
    self.redrawTrace()

  def redrawTrace(self):
    self.mainPlot.clear()
    if self.activeTrace is None:
      self.mainPlot.plot([7,152,3,4,5,6,7])
    else:
      self.mainPlot.plot(self.activeTrace.getSingleTrace(0))
    self.canvas.draw()

  def create_menu(self):
    self.menubar = tk.Menu(self.master)
    filemenu = tk.Menu(self.menubar,tearoff=0)
    filemenu.add_command(label="Open Trace",command=self.open_trace)
    self.menubar.add_cascade(label="File",menu=filemenu)
    self.master.config(menu=self.menubar)

  def create_widgets(self):
    self.f = Figure(figsize=(8,6),dpi=100)
    self.mainPlot = self.f.add_subplot(111)
    self.canvas = FigureCanvasTkAgg(self.f,self.master)
    self.canvas.draw()
    self.canvas_tk = self.canvas.get_tk_widget().pack(side=tk.BOTTOM,fill=tk.BOTH,expand=True)
    
  def createNavbar(self):
    self.navFrame = tk.Frame(self.master,height=100)
    self.entry["btnPrevTrace"] = tk.Button(self.navFrame,text="<")
    self.entry["btnPrevTrace"].pack(side=tk.LEFT)
    self.entry["txtTraceSelect"] = tk.Entry(self.navFrame,width=10)
    self.entry["txtTraceSelect"].pack(side=tk.LEFT)
    self.entry["btnNextTrace"] = tk.Button(self.navFrame,text=">")
    self.entry["btnNextTrace"].pack(side=tk.LEFT)
    self.entry["btnRefreshTrace"] = tk.Button(self.navFrame,text="R")  # refresh (multi trace, etc)
    self.entry["btnRefreshTrace"].pack(side=tk.LEFT)
    lblOffset = tk.Label(self.navFrame,text="O:")
    lblOffset.pack(side=tk.LEFT)
    self.entry["txtOffset"] = tk.Entry(self.navFrame,width=10)
    self.entry["txtOffset"].pack(side=tk.LEFT)
    lblOffset = tk.Label(self.navFrame,text="N:")
    lblOffset.pack(side=tk.LEFT)
    self.entry["txtSamplecount"] = tk.Entry(self.navFrame,width=10)
    self.entry["txtSamplecount"].pack(side=tk.LEFT)
    self.entry["btnRefreshFilters"] = tk.Button(self.navFrame,text="Refresh")  # refresh (multi trace, etc)
    self.entry["btnRefreshFilters"].pack(side=tk.LEFT)
    self.navFrame.pack(side=tk.TOP,fill=tk.X,expand=True)

if __name__ == "__main__":
  root = tk.Tk()
  root.title("sparkgap")
  root.geometry("800x600")
  app = Application(master=root)
  app.mainloop()

