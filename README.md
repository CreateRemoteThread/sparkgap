# sparkgap

_documentation is wip_

Sparkgap is a set of scripts and a python library to assist in hardware control and execution of side channel and fault injection attacks. It includes the following components:

- lib/: the sparkgap library
- cpa.py: executes standard correlation power analysis
- dpa.py: executes standard differential power analysis
- nddla.py: executes Benjamin Timon's 2019 attack (https://tches.iacr.org/index.php/TCHES/article/view/7387)
- capturebuddy.py: helper to capture data from different frontends
- plot.py: inspect captured waves, plot various aspects of them for manual analysis
- preprocessor.py: scripted preprocessor engine for aligning and noise removal etc
- experiments/
  - *.cmd: preprocessor scripting files
  - files in here are work in progress, and may arbitrarily not work / brick things

This can be installed like a standard Python library:

```
python3 -m pip install -r requirements.txt
cd lib/
python3 setup.py install --user
```

The code is provided as-is, pull requests welcome :)
