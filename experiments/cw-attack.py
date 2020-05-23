#!/usr/bin/python3

import sys
import chipwhisperer as cw
import chipwhisperer.analyzer as cwa

proj = cw.open_project(sys.argv[1])
print("Loaded")
attack = cwa.cpa(proj,cwa.leakage_models.sbox_output)
attack.points_range=[3000,13000]
print("Begin!")
results = attack.run()
print(results.find_maximums())
print(results.best_guesses())
