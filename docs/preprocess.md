# Signal Preprocessing

Because this framework is non-synchronous, traces will be desynchronised with one another. The "preprocessor.py" tool offers two key methods of noise reduction: sum-of-absolute-difference minimization and peak correlation finding. Support is built-in for using an operational 

To demonstrate this, let's review a power trace from a smartcard running a variant MILENAGE. To begin, let us plot three traces atop one another. To show the signal clearly, let's use a first order low pass filter, with a cut off at 600khz and a sample rate of 125MSPS, and zomming in on a power consumption peak:

./plot.py -f ~/data/example1.traces -c 1,2,3 --lowpass 600000,125000000,1 -o 50000 -n 5000:

[misaligned](imgs/prs-lowpass-misaligned.png)

The traces are too misaligned to conduct a useful statistical attack, so let's use the preprocessor tool to clean this up. We can first implement a "coarse" max-correlation alignment, as follows:

./preprocessor.py -f ~/data/example1.traces -w ~/data/example1-step1-out -c experiments/pr-scfast-coarse.cmd

You need to edit the pr-scfast-coarse.cmd to pick a "reference window" and a corresponding "reference trace". You can see that now, the peaks are aligned, but the individual samples are still not:

We can then implement a "fine-grained" alignment pass, using pr-scfast-fine.cmd:

[fine alignment](imgs/prs-fine-align.png)

Now, we are (maybe, idk, not working here but WIP) ready to perform statistical analysis.

