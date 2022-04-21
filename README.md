# sparkgap

[quickstart](docs/quickstart.md) | [develop](docs/quickstart-dev.md) | [noise_preprocessing](docs/noisesim.md)

Sparkgap is a major refactor of my previous SCA and FI code. This provides a more consistent UI experience (console instead of paragraph-length command-lines), better self-contained documentation and a single unified support module for both FI and SCA tasks.

This toolkit contains:

- cpa.py, wrapper for correlation attacks
- dpa.py, wrapper for differential attacks
- plot.py, a simple trace visualizer
- preprocessor.py, a signal alignment tool
- capturebuddy.py, wrapper for signal acquisition jobs
  - frontends/*, wrapper scripts for various acquisition frontends
    - ps6000.py, for PicoScope 6xxx
    - ps2000.py, for PicoScope 2xxx
    - rigol.py, for Rigol DS1xxx over Ethernet
    - rigolusb.py, for Rigol DS1xxx over USB (alot faster!)
    - bladerf.py, EXPERIMENTAL DO NOT USE
  - drivers/*, wrapper scripts for logic control drivers
- triggerbuddy.py, control script for TriggerBuddy FPGA module
- support/*, a single support package for FI and SCA
- support/attacks/*, distinguisher and correlation modeling
- experiments/*, in-progress and successful attacks
- docs/*, self-contained markdown documentation

These tools should be used in a workflow. A quick start workflow is documented [here](docs/quickstart.md), and more documentation can be found in the docs/ folder. You should also read [this](docs/quickstart-dev.md) to extend the framework.

The code is provided as-is, pull requests welcome :)
