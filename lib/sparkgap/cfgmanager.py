#!/usr/bin/env python3

class CfgManager:
  def __init__(self):
    print("Initializing CfgManager")
    self.vars = {}

  def setVariable(self,varname,varvalue):
    self.vars[varname] = varvalue

  def getVariable(self,varname):
    return self.vars[varname]

  def getOptionalVariable(self,varname,default):
    if varname in self.vars.keys():
      return self.vars[varname]
    else:
      return default
