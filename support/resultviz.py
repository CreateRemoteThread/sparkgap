#!/usr/bin/env python3

import tkinter as tk
from tkinter import *
import matplotlib

matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class VisualizerApp(tk.Tk):
  def __init__(self):
    super().__init__()
    self.title("TkInter test")
    fig = Figure()
    self.fig = fig
    self.fig_cnv = FigureCanvasTkAgg(fig,self)
    self.mainPlot = fig.add_subplot(111)
    self.fig_cnv.get_tk_widget().pack(side=tk.LEFT,fill=tk.BOTH,expand=1)
    self.rightPanel = Frame(self,width=100)
    self.rightPanel.pack(side=tk.RIGHT)
    self.redraw_button = Button(self.rightPanel,text="Redraw",command=self.render)
    self.redraw_button.pack(side=tk.BOTTOM)
    self.graphData = {}
    self.renderOptions = {}
    self.drawnFragments = 0

  def addData(self,keyPos,keyGuess,corrValue):
    self.graphData[keyPos] = (keyGuess,corrValue)
    self.renderOptions[keyPos] = tk.IntVar()
    checklbl = "Key Fragment %d" % keyPos
    f = tk.Checkbutton(self.rightPanel,text=checklbl,variable=self.renderOptions[keyPos],onvalue=1,offvalue=0)
    if self.drawnFragments < 24:
      f.select()
      self.drawnFragments += 1
    f.pack(side=tk.TOP)

  def render(self):
    self.mainPlot.clear()
    for bytePos in self.graphData.keys():
      if self.renderOptions[bytePos].get() == 1:
        (keyGuess,corrValue) = self.graphData[bytePos]
        self.mainPlot.plot(keyGuess,corrValue)
      else:
        pass
        # print("Not drawing!")
    self.fig_cnv.draw()

if __name__ == "__main__":
  print("This is for testing only, invoke this from within cpa.py")
  app = VisualizerApp()
  app.addData(0,[1,2,3],[4,5,6])
  app.render()
  app.mainloop()
