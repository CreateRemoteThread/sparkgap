#!/usr/bin/env python3

import os
import site
import sys

from distutils.sysconfig import get_python_lib

from setuptools import setup

setup(name="sparkgap",packages=["sparkgap","sparkgap.attacks","sparkgap.glitcher","sparkgap.preprocessor"])

