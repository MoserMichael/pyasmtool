#!/usr/bin/env python3

import prettytrace

def fac_iter(arg_n: int) -> int:
    res = 1
    for cur_n in range(1,arg_n+1):
        res *= cur_n
    return res

fac_iter = prettytrace.TraceMe(fac_iter)

print( "fac_iter(7):", fac_iter(7))
