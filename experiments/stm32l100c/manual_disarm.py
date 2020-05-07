#!/usr/bin/env python3

import chipwhisperer as cw

print("Manual disarm")

scope = cw.scope()
scope.dis()
