# emu

This folder contains experiments for software-emulated side channel, using Ledger-Donjon's Rainbow framework. The example executable is DES. You can compile this with:

arm-none-eabi-gcc -nostdlib -o des.elf des.c

Now use des_loader.py (or equivalent) to generate traces. You need to modify:

- Where the data lives:
  - KEY_ADDR
  - DATA_ADDR
  - OUT_ADDR
- Where the key function is:
  - DODES_START
  - DODES_END

