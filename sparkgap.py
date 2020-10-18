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
    self.create_widgets()

  def open_trace(self):
    fn = tk.filedialog.askopenfilename(initialdir="~/",title="Select trace...",filetypes=(("Trace File","*.traces"),))
    self.activeTrace = support.filemanager.TraceManager(fn)
    print(fn)

  def redrawTrace(self):
    self.mainPlot.clear()
    # self.mainPlot.plot([7,152,3,4,5,6,7])
    self.canvas.draw()

  def create_menu(self):
    self.menubar = tk.Menu(self.master)
    filemenu = tk.Menu(self.menubar,tearoff=0)
    filemenu.add_command(label="Open Trace",command=self.open_trace)
    # filemenu.add_command(label="Close Trace",command=self.close_trace)
    # filemenu.add_command(label="Exit",command=self.exit_app)
    self.menubar.add_cascade(label="File",menu=filemenu)
    self.master.config(menu=self.menubar)

  def create_widgets(self):
    self.f = Figure(figsize=(8,6),dpi=100)
    self.mainPlot = self.f.add_subplot(111)
    # self.mainPlot.plot([0,1,2,3,4,5])
    self.canvas = FigureCanvasTkAgg(self.f,self)
    self.canvas.draw()
    self.canvas_tk = self.canvas.get_tk_widget().pack(side=tk.BOTTOM,fill=tk.BOTH,expand=True)
    # self.nav_toolbar = NavigationToolbar2TkAgg(canvas,self)
    # self.nav_toolbar.update()
    # self.canvas._tkcanvas.pack(side=tk.TOP,fill=tk.BOTH,expand=True)
    

  def start_w_glitch(self):
    print("Starting Glitch Window")

if __name__ == "__main__":
  root = tk.Tk()
  root.geometry("800x600")
  app = Application(master=root)
  app.mainloop()

