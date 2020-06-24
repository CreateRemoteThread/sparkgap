# Quick Start Guide Development

![Setup Picture](imgs/quickstart/docs-commit.png)

This page documents the software architecture of the sparkgap project, to support development. If you want to implement additional frontends/drivers, this is the place.

## capturebuddy.py

Capturebuddy is a generic frontend for capturing. It uses a frontend (specified by -f) to control the oscilloscope and a driver (specified by -d) to control the target board. It does a sketchy dynamic import, as below:

```
def acquireInterface(interfacename):
  global fe
  try:
    exec("from frontends.%s import CaptureInterface; fe = CaptureInterface()" % interfacename,globals())
  except:
    print("Unable to acquire interface '%s'" % interfacename)
    fe = None
```

Once it's got both the frontend and driver, it will initialize both the frontend and driver (passing the frontend object to the driver):

```
  fe.init()
  drv.init(fe)
```

Then, it will repeatedly call the driver's "drive" function, followed by the frontend's "capture" function:

```
  for i in range(0,config["tracecount"]):
    print("Running job: %d/%d. %d missed" % (i,config["tracecount"],missedCount))
    if config["tlva"] is None:
      (next_rand, next_autn) = drv.drive(None) # should return (plaintext, ciphertext)
    else:
      if random.randint(0,100) % 2 == 0:
        (next_rand, next_autn) = drv.drive([0xAA] * 16)
      else:
        (next_rand, next_autn) = drv.drive(None)
    time.sleep(3.0)
    dataA = fe.capture() # should return numpy float array
```

Note that it's completely up to the driver to arm the frontend: if you get no captures, check your trigger conditions.

Then, if CONFIG_WRITEFILE is set (via set writefile="/tmp/blah"), it will save the captured traces to the specified file, appending .traces and .data/ as necessary. If the file is already present, it will fail, wasting your hours of progress (todo fix).

## preprocessor.py / plot.py

The preprocessor is the epitome of dirty hack (and this goes for plot.py, suffering precisely the same problem of a monolithic, old codebase), but a framework is being laid to allow clean modular code. Currently, the preprocessor needs a source file (via -f) and a destination file (via -w, will auto-create .traces and .data/).

If no command file is specified (via -c), it will enter an interactive mode, where you can set variables (via set varname=blah). Note the "blah" is just eval'ed, by design:

```
def doSingleCommand(cmd,tm_in):
  tokens = cmd.split(" ")
  if tokens[0] == "set" and len(tokens) >= 2:
    tx = " ".join(tokens[1:])
    (argname,argval) = tx.split("=")
    CFG_GLOBALS[argname] = eval(argval)
```

A strategy argument is required (via set strategy=), and depending on the strategy, it will branch off into a number of processor functions, all of which have access to the CFG_GLOBALS array (in the current design it's just accessed via a global, todo make a ConfigManager object and pass it around).

No support is implemented for "save-in-place", by design - the idea is that you can test changes, and "roll back" to an earlier state if you need to.

## cpa.py / dpa.py

The "attack code" modules are extremely straightforward. They require:

- a source file (via -f)
- an attack model (via -a)

Optionally, they take:

- an offset to start processing from (via -o)
- the number of slides from the offset to process (via -n)

We then load the attack model:

```
cpa.py: 
leakmodel = support.attack.fetchModel(CONFIG_LEAKMODEL)

support.py:
def fetchModel(modelname):
  try:
    exec("from support.attacks.%s import AttackModel; fe = AttackModel()" % modelname,globals())
    return fe
  except:
    print("Could not load attack model '%s'" % modelname)
    usage()
    sys.exit(0)
```

The model represents the power leakage "guess" corresponding to each attack: for example, AES_SboxOut_HW will calculate the expected Hamming weights for the first-round SBox out in an 8-bit model (using cpa.py) or provide a distinguisher for the same (for dpa.py and tlva.py).