#!/usr/bin/env python3


class DriverInterface():
  def __init__(self):
    self.config = {}
    # reserved names: samplecount,tracecount,trigger
    pass

  def init(self):
    pass

  def drive(self,in_text=None):
    return (in_text,out_text)

  def close(self):
    pass
