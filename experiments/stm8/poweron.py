#!/usr/bin/env python3

import chipwhisperer as cw

scope = cw.scope()
scope.io.target_pwr = True
scope.dis()
