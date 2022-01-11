#!/usr/bin/env python3

import pyasmtools
import sys

def compute_historgram(file_name):
    with open(file_name,'r') as file:
        text = file.read()

        histo = {}
        for ch in text:
            if not ch in histo:
                histo[ch] = 1
            else:
                histo[ch] += 1

        for ch in histo.keys():
            print("char:", repr(ch), "frequency:", histo[ch])

compute_historgram = pyasmtools.TraceMe(compute_historgram, out=sys.stdout) # out=sys.stdout - redirects trace output to sys.stdout

compute_historgram("./example_text.txt")

