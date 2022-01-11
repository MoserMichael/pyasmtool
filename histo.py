#!/usr/bin/env python3

import pyasmtools 

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

#compute_historgram(__file__)
print( "pyasmtools.prettydis(compute_historgram, show_opcode_as_links=True):", pyasmtools.prettydis(compute_historgram, show_opcode_as_links=True) )

