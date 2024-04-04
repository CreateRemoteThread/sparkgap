#!/usr/bin/env python3

from Crypto.Cipher import DES

key = b'\xdf\xa2\xf7\x41\xd7\xb8\x69\xfa'
# P: 788878666439593e
# C: 13d223cae96297d6

def pad(text):
        while len(text) % 8 != 0:
            text += '\x00'
        return text

des = DES.new(key, DES.MODE_ECB)

text1 = b"\x78\x88\x78\x66\x64\x39\x59\x3e"

# padded_text = pad(text1)

encrypted_text = des.encrypt(text1)

import binascii
print(binascii.hexlify(encrypted_text))

print(binascii.hexlify(des.decrypt(encrypted_text)))
