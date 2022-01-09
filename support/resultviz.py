#!/usr/bin/env python3

import tkinter as tk
import matplotlib

matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class VisualizerApplication(tk.Tk):
  def __init__(self):
    super().__init__()
    self.title("TkInter test")
    fig = Figure()
    fig_cnv = FigureCanvasTkAgg(fig,self)
    axes = fig.add_subplot()
    axes.plot([1,2,3,4,5])
    fig_cnv.get_tk_widget().pack(side=tk.TOP,fill=tk.BOTH,expand=1)

  def plotData(self,data,round,annotations):
    # test

if __name__ == "__main__":
  print("This is for testing only, invoke this from within cpa.py")
  app = VisualizerApp()
  app.mainloop()
