# emu

This folder contains experiments for software-emulated side channel, using Ledger-Donjon's Rainbow framework. The example executable is AES (also DES but DES impl is data dependent). You can compile this with:

arm-none-eabi-gcc -nostdlib -o aes.elf aes.c

Now use aes_loader.py (or equivalent) to generate traces. You need to modify:

- Where the data lives:
  - KEY_ADDR
  - DATA_ADDR
  - OUT_ADDR
- Where the key function is:
  - DOAES_START (or look for emu.start)
  - DOAES_END

Then call aes_loader like this:

./aes_loader.py -f ./aes.elf -w /var/tmp/blabla.hdf

This generates 250 traces with a fixed key into /var/tmp/blabla.hdf, creating data for the aes implementaiton only, and prints the key out at the end.

Now CPA it out with something like:

./cpa.py -f aes.elf -a AES_SboxOut_HW

The emulation doesn't generate noise in aes_loader.py - the correlation is strong enough you can just correlation analysis the entire length of the trace and it will work.
