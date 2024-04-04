#!/usr/bin/env python3

import cProfile

in_num = 0x12345678

def method1(number):
  return bin(number).count("1")

def method2(number):
  totalI = 0
  for i in range(0,32):
    totalI += (number >> i) & 1
  return totalI

def test_method1():
  for i in range(0,50000):
    method1(0x12345678)

def test_method2():
  for i in range(0,50000):
    method2(0x12345678)

cProfile.run("test_method1()")
cProfile.run("test_method2()")
