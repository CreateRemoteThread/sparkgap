#!/usr/bin/env python3

class model:
  def __init__(self):
    self.hw_table_length = 2 ** 16
    self.hw_table = [0] * self.hw_table_length
    self.init_hw_table()

  @staticmethod
  def hw(value):
    return bin(value).count('1')

  def init_hw_table(self):
    for i in range(self.hw_table_length):
      self.hw_table[i] = self.hw(i)

  def leak(self, value):
    return self.hw_table[value & 0xffff] + self.hw_table[value >> 16 & 0xffff]
