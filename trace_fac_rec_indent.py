#!/usr/bin/env python3

import pyasmtools


def fac(arg_n):
    if arg_n == 1:
        return arg_n
    return arg_n * fac(arg_n - 1)

fac = pyasmtools.TraceMe(fac, trace_indent=True)

print( "fac(7):", fac(7))
